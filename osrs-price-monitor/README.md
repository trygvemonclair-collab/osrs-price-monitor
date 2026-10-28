# OSRS price monitor

Automatic daily collection of 24h price data for seven OSRS items, using the official community API on OSRS Wiki. The public GitHub Pages site is sourced from `/docs` on the `main` branch. **Run Actions > Update OSRS prices > Run workflow at least once before opening the page.**

Data fields: `avgHighPrice` means instant buys; `avgLowPrice` means instant sells. These are historical execution averages and not a live order book.

Settings > Actions > General > Workflow permissions: allow **Read and write permissions** if repository workflow has no permission to commit. Public repo is required for the simplest free Pages setup. Github Actions scheduled jobs may be delayed. See official GitHub and OSRS Wiki documentation.
