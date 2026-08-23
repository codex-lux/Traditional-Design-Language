.PHONY: check counts

check:
	python3 build/check_all.py

counts:
	python3 build/gen_readme_counts.py
