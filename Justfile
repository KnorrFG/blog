serve:
  pipenv run python manage -s

upload:
  pipenv run python manage -d /tmp/blog_dist
  rsync --progress -az --update --delete /tmp/blog_dist/ vserver:apps/homepage/
