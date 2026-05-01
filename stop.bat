@echo off
echo Stopping AcmeCloud Support Agent...
powershell -Command "$ports = @(8501, 8080); foreach ($port in $ports) { $p = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; if ($p) { foreach ($id in $p) { Write-Host \"Killing process on port $port (PID: $id)...\"; Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } } else { Write-Host \"No process on port $port.\" } }"
echo AcmeCloud Support Agent stopped.
