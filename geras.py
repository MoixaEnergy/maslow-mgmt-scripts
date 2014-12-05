import argparse, requests, json, itertools, re, datetime, csv
from urllib.parse import urlencode

class GroupApi:
  device_subseries = [["current", "battery"],
                      ["current", "mains"],
                      ["current", "networkPos"],
                      ["current", "pv"],
                      ["voltage", "battery"],
                      ["voltage", "mains"],
                      ["voltage", "network"],
                      ["voltage", "pv"],
                      ["clamps" , "ac"],
                      ["clamps" , "ac2"]]

  def define(self, args):
    series = ['/'.join(itertools.chain([dev],subs)) for dev in args.device for subs in self.device_subseries]
    res = requests.post('https://geras.1248.io/group',
                        auth=(args.apikey, ''),
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps({"group_id": args.name,
                                         "list": series}))

    print(res.text)

  def list(self, args):
    res = requests.get('https://geras.1248.io/group',
                       auth=(args.apikey, ''))
    res_obj = json.loads(res.text)
    for group in res_obj.keys():
      if group.find(args.match) >= 0:
        print(group)

  def delete(self, args):
    res = requests.delete('https://geras.1248.io/group/{name}'.format(name=args.name),
                          auth=(args.apikey, ''))

    print(res.text)

  def detail(self, args):
    res = requests.get('https://geras.1248.io/group/{name}'.format(name=args.name),
                       auth=(args.apikey, ''))
    print(res.text)

  def add_as_subparser(self, subparsers, name):
    parser = subparsers.add_parser(name)
    parser.add_argument("-a", "--apikey", required=True)
    subparser = parser.add_subparsers(help="manage groups of devices")

    define_parser = subparser.add_parser("define")
    define_parser.add_argument("name", help="name of the group to create/modify")
    define_parser.add_argument("device", nargs='+')
    define_parser.set_defaults(func=self.define)

    list_parser = subparser.add_parser("list")
    list_parser.add_argument("-m", "--match", help="group name substring to match", required=False, default="")
    list_parser.set_defaults(func=self.list)

    delete_parser = subparser.add_parser("delete")
    delete_parser.add_argument("name", help="group to delete")
    delete_parser.set_defaults(func=self.delete)

    details_parser = subparser.add_parser("detail")
    details_parser.add_argument("name", help="group name")
    details_parser.set_defaults(func=self.detail)

class ShareApi:
  def list(self, args):
    res = requests.get("https://geras.1248.io/share",
                       auth=(args.apikey, ''))
    print(res.text)

  def define(self, args):
    res = requests.post("https://geras.1248.io/share",
                        auth=(args.apikey, ''),
                        headers={"Content-Type": "application/json"},
                        data=json.dumps({"key": args.key,
                                         "share_id": args.name,
                                         "query": {
                                           "pattern": "",
                                           "group": args.group,
                                         }}))
    print(res.text)

  def delete(self, args):
    res = requests.delete("https://geras.1248.io/share/{name}".format(name=args.name),
                          auth=(args.apikey, ''))
    print(res.text)

  def add_as_subparser(self, subparsers, name):
    parser = subparsers.add_parser(name)
    parser.add_argument("-a", "--apikey", required=True)
    subparser = parser.add_subparsers(help="manage shares")

    list_parser = subparser.add_parser("list")
    list_parser.set_defaults(func=self.list)

    define_parser = subparser.add_parser("define")
    define_parser.add_argument("name", help="name of the share to create/modify")
    define_parser.add_argument("group", help="group to share")
    define_parser.add_argument("key", help="key for accessing share")
    define_parser.set_defaults(func=self.define)

    delete_parser = subparser.add_parser("delete")
    delete_parser.add_argument("name", help="name of the share to delete")
    delete_parser.set_defaults(func=self.delete)

def parse_datetime(s):
  return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M")

class ExportApi:
  def device(self, args):
    print("device")
    print(args.device)
    print(args.from_d)
    print(args.to)

  def all(self, args):
    t_from = int(args.from_d.timestamp())
    t_to   = int(args.to.timestamp())
    res = requests.get("https://geras.1248.io/share/{share}/series/".format(share=args.share),
                       params={"start": t_from, "end": t_to, "pattern": "/#", 
                               "rollup": "avg", "interval": "1m"},
                       headers={'accept-encoding': 'identity'},
                       auth=(args.key, ''))

    res_obj = json.loads(res.text)
    times = sorted(set([datetime.datetime.fromtimestamp(entry["t"]) for entry in res_obj["e"]]))
    paths = sorted(set([entry["n"] for entry in res_obj["e"]]))
    d = dict()
    for entry in res_obj["e"]:
      t = datetime.datetime.fromtimestamp(entry["t"])
      if t not in d: d[t] = {}
      d[t].update({entry["n"]:entry["v"]})

    with open(args.out, 'w', newline='') as outfile:
      writer = csv.DictWriter(outfile, ["Time"] + paths)
      writer.writeheader()
      for t in times:
        row = {"Time": t}
        row.update(d.get(t, {}))
        print(row)
        writer.writerow(row)

  def add_as_subparser(self, subparsers, name):
    parser = subparsers.add_parser(name)
    parser.add_argument("-s", "--share", required=True)
    parser.add_argument("-k", "--key", required=True)
    parser.add_argument("-g", "--group", required=True)
    parser.add_argument("-o", "--out", required=True)
    subparser = parser.add_subparsers(help="export data")

    device_parser = subparser.add_parser("device")
    device_parser.add_argument("name", help="name of device")
    device_parser.add_argument("from_d", type=parse_datetime, metavar="from")
    device_parser.add_argument("to", type=parse_datetime)
    device_parser.set_defaults(func=self.device)

    all_parser = subparser.add_parser("all")
    all_parser.add_argument("from_d", type=parse_datetime, metavar="from")
    all_parser.add_argument("to", type=parse_datetime)
    all_parser.set_defaults(func=self.all)

def main():
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers(help="sub-command")

  GroupApi().add_as_subparser(subparsers, "group")
  ShareApi().add_as_subparser(subparsers, "share")
  ExportApi().add_as_subparser(subparsers, "export")

  args = parser.parse_args()
  args.func(args)

if __name__ == "__main__":
  main()
