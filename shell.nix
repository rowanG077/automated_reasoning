with ((import (fetchTarball {
  name = "nixpkgs-master-2021-09-30";
  url = "https://github.com/NixOS/nixpkgs/archive/7017a662007a2d7becd3b0298b341bcaea2d36d3.tar.gz";
  sha256 = "0ykahd48ygmg9hxy18bb017906dlv92ln9ajcdl6zglcfy0c6jj1";
}) {}));
  let extensions = (with pkgs.vscode-extensions; [
      ms-vsliveshare.vsliveshare
      bbenoist.nix
      redhat.vscode-yaml
    ] ++ pkgs.vscode-utils.extensionsFromVscodeMarketplace [{
      name = "smt-lib-syntax";
      publisher = "martinring";
      version = "0.0.1";
      sha256 = "Vmt1gFRai52WmmrqHZKxR0VbV4AdT0VtEX3p8eV7CNo=";
    }] ++ pkgs.vscode-utils.extensionsFromVscodeMarketplace [{
      name = "vscode-nusmv";
      publisher = "liamwalsh98";
      version = "0.0.1";
      sha256 = "subyhXjhV9xYbRuB5iVLxNFR4Fh2HXKpyah13IBEU9s=";
    }]);

  nuSMV = pkgs.callPackage ./nuSMV.nix { };

  vscode-with-extensions = pkgs.vscode-with-extensions.override {
    vscodeExtensions = extensions;
  };
in pkgs.mkShell {
  packages = [
    vscode-with-extensions
    nuSMV
    pkgs.yices
    pkgs.prover9
    pkgs.python38
    pkgs.python38Packages.setuptools
    pkgs.python38Packages.z3
    pkgs.python38Packages.pycairo
  ];
}
