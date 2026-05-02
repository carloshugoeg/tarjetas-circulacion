$ErrorActionPreference = "Stop"

$dockerBin = "C:\Program Files\Docker\Docker\resources\bin"
$docker = Join-Path $dockerBin "docker.exe"

if (-not (Test-Path $docker)) {
    throw "Docker no se encontro en $docker. Verifica la instalacion de Docker Desktop."
}

$env:PATH = "$dockerBin;$env:PATH"

& $docker compose up --build -d
& $docker compose ps
