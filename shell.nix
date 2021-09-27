with ((import (fetchTarball {
  name = "nixpkgs-master-2021-05-12";
  url = "https://github.com/NixOS/nixpkgs/archive/refs/tags/21.05.tar.gz";
  sha256 = "1ckzhh24mgz6jd1xhfgx0i9mijk6xjqxwsshnvq789xsavrmsc36";
}) {}));
  let extensions = (with pkgs.vscode-extensions; [
      ms-vsliveshare.vsliveshare
      ms-python.python
      bbenoist.Nix
      redhat.vscode-yaml
    ] ++ pkgs.vscode-utils.extensionsFromVscodeMarketplace [{
      name = "smt-lib-syntax";
      publisher = "martinring";
      version = "0.0.1";
      sha256 = "Vmt1gFRai52WmmrqHZKxR0VbV4AdT0VtEX3p8eV7CNo=";
    }]);

  vscode-with-extensions = pkgs.vscode-with-extensions.override {
    vscodeExtensions = extensions;
  };
in pkgs.mkShell {
  packages = [
    vscode-with-extensions
    pkgs.yices
    pkgs.prover9
    pkgs.python38
    pkgs.python38Packages.setuptools
    pkgs.python38Packages.z3
  ];
}
