# Activate virtual environment
.\Scripts\activate

pyinstaller `
  --onefile `
  --add-data "src;src" `
  --add-data "imgs;imgs" `
  --hidden-import matplotlib.backends.backend_tkagg `
  --hidden-import matplotlib.backends.backend_agg `
  --clean `
  --windowed `
  --name "SimuladorFotoelectrico" `
  main.py
