$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$cacheDir = Join-Path $projectRoot ".docker-cache"
$images = @(
    @{ Source = "docker://docker.io/library/postgres:15-alpine"; Archive = "postgres-15-alpine.tar"; Tag = "postgres:15-alpine" },
    @{ Source = "docker://docker.io/library/python:3.11-slim"; Archive = "python-3.11-slim.tar"; Tag = "python:3.11-slim" },
    @{ Source = "docker://docker.io/library/node:20-alpine"; Archive = "node-20-alpine.tar"; Tag = "node:20-alpine" }
)

New-Item -ItemType Directory -Force -Path $cacheDir | Out-Null

Write-Host "Quitando credenciales de Docker Hub para evitar tokens corruptos..."
docker logout | Out-Null

Write-Host "Verificando skopeo en Ubuntu WSL..."
$hasSkopeo = wsl -d Ubuntu -- bash -lc "command -v skopeo >/dev/null 2>&1; echo `$?"
if ($hasSkopeo.Trim() -ne "0") {
    Write-Host "Instalando skopeo en Ubuntu WSL..."
    wsl -d Ubuntu -u root -- bash -lc "apt-get update && apt-get install -y skopeo"
}

foreach ($image in $images) {
    $archivePath = Join-Path $cacheDir $image.Archive
    $wslArchivePath = "/mnt/c/" + ($archivePath.Substring(3) -replace "\\", "/")
    Write-Host "Descargando $($image.Tag) via skopeo..."
    wsl -d Ubuntu -- bash -lc "skopeo copy --retry-times 5 --override-arch amd64 $($image.Source) docker-archive:$wslArchivePath`:$($image.Tag)"

    Write-Host "Cargando $($image.Tag) en Docker..."
    docker load -i $archivePath
}

Write-Host "Listo. Ahora puedes ejecutar: docker compose up --build -d"
