

mount_s3:
	python main.py mounts3 --name juicefss3

mount_uplink:
	python main.py mountuplink --name juicefsuplink

jfs_bench_prod_s3:
	python main.py --is-prod

jfs_bench_prod_uplink:
	python main.py --run-new --is-prod

login_psql:
	psql --host=myjuicefs.cvosic8aio60.us-east-2.rds.amazonaws.com --username=postgres --dbname=postgres
