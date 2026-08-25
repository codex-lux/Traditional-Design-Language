.PHONY: check counts

check:
	python3 build/check_all.py

counts:
	python3 build/gen_readme_counts.py

# --- The Workbench (WP-5.2) -------------------------------------------------
# Serve the built app + JSON API on 127.0.0.1:8177. Requires:
#   pip install -r workbench/requirements.txt
#   (cd workbench/app && npm install && npm run build)   # once, or after app changes
workbench:
	python3 -m workbench.server

# Dev mode: run these in two terminals (vite proxies /api to 8177, so no CORS):
#   uvicorn workbench.server.app:app --reload --port 8177
#   cd workbench/app && npm run dev
workbench-dev:
	@echo "terminal 1:  uvicorn workbench.server.app:app --reload --port 8177"
	@echo "terminal 2:  cd workbench/app && npm run dev"

workbench-test:
	python3 -m pytest workbench/server/tests -q

.PHONY: workbench workbench-dev workbench-test
