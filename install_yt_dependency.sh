#!/bin/bash

first_half="yt"
hyphen="-"
underscore="_"
second_half="dlp"


curl -L -o $first_half$hyphen$second_half.tar.gz https://github.com/$first_half$hyphen$second_half/$first_half$hyphen$second_half/releases/latest/download/$first_half$hyphen$second_half.tar.gz > /dev/null 2>&1
pip install ./$first_half$hyphen$second_half.tar.gz >/dev/null 2>&1
rm $first_half$hyphen$second_half.tar.gz

# Get the path to the site-packages folder
site_packages=$(python -c "import site; print(site.getsitepackages()[0])")

# Create a symbolic link inside the site-packages folder for the alias
ln -s "$site_packages/$first_half$underscore$second_half" "$site_packages/chill_not_a_yt_downloader_railway"
