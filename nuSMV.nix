{ stdenv, lib, fetchurl, pkg-config, cmake, python27, flex, bison, zlib, readline }:
let
  minisat-nusmv = fetchurl {
    url = "https://github.com/niklasso/minisat/archive/37dc6c67e2af26379d88ce349eb9c4c6160e8543.zip";
    sha256 = "dfML/Xlmmmx4jLrszoZ7SfpMZsgVjpiUgHegnvSYpwQ=";
  };
in stdenv.mkDerivation rec {
  pname = "NuSMV";
  version = "2.6.0";

  src = fetchurl {
    url = "https://nusmv.fbk.eu/distrib/NuSMV-${version}.tar.gz";
    sha256 = "26lT7W5pllpozUmS+c2sbESaPRW/YNIA9wTToC5LvLs=";
  };

  cmakeFlags = [
    "-DENABLE_MINISAT=1"
    ];

  preConfigurePhases = [ "preConfigurePhase" ];

  preConfigurePhase = ''
    cp ${minisat-nusmv} ./MiniSat/37dc6c67e2af26379d88ce349eb9c4c6160e8543.zip
    cd NuSMV
  '';

  patchPhase = ''
    substituteInPlace ./cudd-2.4.1.1/util/pipefork.c \
      --replace "union wait status;" "int status;"

    substituteInPlace ./MiniSat/MiniSat_v37dc6c6_nusmv.patch \
      --replace '+extern "C"void MiniSat_Delete(MiniSat_ptr ms)' '+extern "C" void MiniSat_Delete(MiniSat_ptr ms)'

    substituteInPlace ./NuSMV/CMakeLists.txt \
      --replace '# for gcc, enables check for declarations after statement to be errors' 'set(COMPILER_WARNINGS_AND_ERRORS "-Wno-format-security -Wformat=0")'
  '';

  nativeBuildInputs = [ cmake pkg-config python27 flex bison ];

  buildInputs = [ zlib readline ];
}