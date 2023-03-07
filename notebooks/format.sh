#!/bin/sh

# Make sure this script is executable using chmod +x format.sh
# Then just run it with the following command line args, for example:
# ./format.sh "glucose-part06.ipynb" "Post 6: bla bla" "2023-03-06-data_part06.html"

nb=$1 # jupyter notebook name
title=$2 # post title
filename=$3 # new file name

# Convert to html
jupyter nbconvert --to html $nb

# Add header
echo "---\nlayout: post\ntitle: "$title"\n---\n\n\n{% raw %}\n$(cat ${nb%.ipynb}.html)" > ${nb%.ipynb}.html

# Add the last line to end of file
echo '{% endraw %}' >> ${nb%.ipynb}.html

# Convert image paths (find ../assets/images/ and replace with /sugar/assets/images/)
sed -i "" "s#../assets/images/#/sugar/assets/images/#g" ${nb%.ipynb}.html

mv ${nb%.ipynb}.html ../_posts/$filename
