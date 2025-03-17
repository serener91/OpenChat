docker build --no-cache -t app:v1 -f app.Dockerfile .
docker build --no-cache -t task:v1 -f task.Dockerfile .
docker build --no-cache -t msg:v1 -f msg.Dockerfile .
docker build --no-cache -t db:v1 -f db.Dockerfile .
docker build --no-cache -t backend:v1 -f backend.Dockerfile .

docker rmi app:v1 task:v1 msg:v1 db:v1 backend:v1