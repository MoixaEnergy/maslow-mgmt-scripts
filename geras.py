import argparse, requests, json, itertools, re

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
    group_parser = subparsers.add_parser("group")
    group_subparsers = group_parser.add_subparsers(help="manage groups of devices")

    group_define_parser = group_subparsers.add_parser("define")
    group_define_parser.add_argument("name", help="name of the group to create/modify")
    group_define_parser.add_argument("device", nargs='+')
    group_define_parser.set_defaults(func=self.define)

    group_list_parser = group_subparsers.add_parser("list")
    group_list_parser.add_argument("-m", "--match", help="group name substring to match", required=False, default="")
    group_list_parser.set_defaults(func=self.list)

    group_delete_parser = group_subparsers.add_parser("delete")
    group_delete_parser.add_argument("name", help="group to delete")
    group_delete_parser.set_defaults(func=self.delete)

    group_details_parser = group_subparsers.add_parser("detail")
    group_details_parser.add_argument("name", help="group name")
    group_details_parser.set_defaults(func=self.detail)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-k", "--apikey", required=True)
  subparsers = parser.add_subparsers(help="sub-command")

  GroupApi().add_as_subparser(subparsers, "group")

  args = parser.parse_args()
  args.func(args)

if __name__ == "__main__":
  main()
