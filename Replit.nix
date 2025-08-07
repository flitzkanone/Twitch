{ pkgs }: {
  deps = [
    pkgs.ffmpeg
    pkgs.yt-dlp
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.python310Packages.openai
  ];
}
