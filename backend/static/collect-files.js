const glob = require('glob');
const fs = require('fs');
const path = require('path');

// Define the root directory where you want to start collecting files
const rootDirectory = path.resolve(__dirname); // Use the current directory as the root

// Define file extensions to exclude (e.g., Python and HTML)
const excludedExtensions = ['.py', '.html'];

// Define a function to collect files recursively
function collectFiles(directory, pattern, excludedExtensions) {
  const options = {
    cwd: directory,
    nodir: true, // Exclude directories
  };

  const files = glob.sync(pattern, options);

  // Filter out files with excluded extensions
  return files.filter((file) => !excludedExtensions.includes(path.extname(file)));
}

// Define the pattern for all files (use "**/*" for recursive search)
const allFilesPattern = '**/*';

// Collect all files except Python and HTML
const collectedFiles = collectFiles(rootDirectory, allFilesPattern, excludedExtensions);
