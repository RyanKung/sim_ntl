default:
	python -m sim
sync:
	rsync -av dev@120.76.233.55:csv/*.csv ./csv/
sync_history:
	rsync -av dev@120.76.233.55:/var/csv/history/*.csv ./history/
notebook:
	jupyter notebook
