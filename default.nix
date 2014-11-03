let
  pkgs = import <nixpkgs> {};
in
  { stdenv ? pkgs.stdenv }:

  stdenv.mkDerivation {
    name = "py-geras";
    version = "0.1.0.0";
    src = ./.;
    buildInputs = with pkgs; with python34Packages; [ python34 requests2 ];
  }
