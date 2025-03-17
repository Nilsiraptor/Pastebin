param(
    [Parameter(Mandatory=$false)]
    [string]$Path = ".\programs.txt",

    [Parameter(Mandatory=$false)]
    [switch]$Silent
)

$successCount = 0
$attemptedCount = 0
$installedCount = 0
$updatedCount = 0
$notFoundCount = 0
$failedCount = 0

if ($Silent) {
    $no_int = "--no-interactivity"
} else {
    $no_int = ""
}

Write-Host "Starting program installation from $($Path)..."

$lines = Get-Content -Path $Path | Where-Object { $_ -and -not ($_.Trim().StartsWith("#")) }

foreach ($p in $lines) {
    $p = $p.Trim()
    if (-not [string]::IsNullOrEmpty($p)) {
        $attemptedCount++
        Write-Host "Installing '$p'..." -ForegroundColor Blue
        try {
            winget install -h -e --no-upgrade $no_int --id $p
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Successfully installed '$p'." -ForegroundColor Green
                $successCount++
            } elseif ($LASTEXITCODE -eq 0x8A150014) {
                Write-Warning "Could not find $p"
                $notFoundCount++
            } elseif ($LASTEXITCODE -eq 0x8A150061) {
                Write-Host "$p is already installed, try to update now..."
                $installedCount++

                winget upgrade -h -e $no_int --id $p

                if ($LASTEXITCODE -eq 0) {
                    Write-Host "Successfully updated '$p'." -ForegroundColor Green
                    $updatedCount++
                }
            }  else {
                Write-Warning "Failed to install '$p'. Exit code: $($LASTEXITCODE)"
                $failedCount++
            }
        } catch {
            Write-Error "An error occurred during the installation of '$p': $($_.Exception.Message)"
            $failedCount++
        }
    }
}

Write-Host ""
Write-Host "Installation Summary:"
Write-Host "---------------------"
Write-Host "Attempted:     $attemptedCount programs"
Write-Host "    Successful:    $($successCount + $updatedCount) programs"
Write-Host "        New:           $successCount programs"
Write-Host "        Updated:       $updatedCount programs"
Write-Host "    Failed:        $($attemptedCount - $successCount - $updatedCount) programs"
Write-Host "        No Update:     $($installedCount - $updatedCount) programs"
Write-Host "        Not Found:     $notFoundCount programs"
Write-Host "        Unknown Error: $failedCount programs"
