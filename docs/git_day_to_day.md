# See what changed
git status
git diff

# Save a checkpoint
git add .
git commit -m "Add news service integration"

# View history
git log --oneline

# Revert a single file to last commit
git checkout -- notebook.ipynb

# Go back to an older commit (read-only peek)
git checkout 616d508
git checkout main   # return to latest