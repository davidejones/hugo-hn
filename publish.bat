@echo off

echo Deleting old publication
@set PubDir=%~dp0public\
@set TreeDir=%~dp0.git\worktrees\public\
call:delPub %PubDir%
if not exist "%PubDir%" mkdir %PubDir%
git worktree prune
IF EXIST "%TreeDir%" (
    del /s /q %TreeDir%
    rmdir /s /q %TreeDir%
)

echo Checking out gh-pages branch into public
git worktree add -B gh-pages public origin/gh-pages

call:delPub %PubDir%

echo Generating site
hugo

echo Updating gh-pages branch
cd public && git add --all && git commit -m "Publishing to gh-pages (publish.bat)"

:: force execution to quit at the end of the "main" logic
exit /B


::--------------------------------------------------------
:: Functions start here
::--------------------------------------------------------

:: Function to clear public folder
:delPub
echo Removing public files
IF EXIST "%~1" (
    del /s /q %~1
    rmdir /s /q %~1
)
exit /B 0
