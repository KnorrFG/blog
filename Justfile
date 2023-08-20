_default:
  @just --list
  
start-server:
  cd /tmp/bloghost && python -m http.server 8080

start-builder:
  pipenv run python blog.py serve

upload:
  pipenv run python blog.py build /tmp/blog_dist
  rsync --progress -az --update --delete /tmp/blog_dist/ vserver:apps/homepage/
