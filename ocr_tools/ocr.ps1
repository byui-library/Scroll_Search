param([string]$ListFile, [string]$OutDir, [int]$MaxDim = 4000)
# OCR each TIFF path in $ListFile with Windows.Media.Ocr; write <OutDir>\<basename>.txt
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics, ContentType = WindowsRuntime]
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, [Type]$t) { $task = $asTaskGeneric.MakeGenericMethod($t).Invoke($null, @($op)); $task.Wait(-1) | Out-Null; $task.Result }
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
$tmp = Join-Path $OutDir ("_tmp_" + $PID + ".png")
foreach ($line in Get-Content $ListFile) {
  $id, $path, $label = $line -split "`t", 3
  if (-not $label) { $label = $path }
  $out = Join-Path $OutDir ($id + ".txt")
  if (Test-Path $out) { continue }
  try {
    $img = [System.Drawing.Image]::FromFile($path)
    $scale = [Math]::Min(1.0, $MaxDim / [Math]::Max($img.Width, $img.Height))
    $w = [int]($img.Width * $scale); $h = [int]($img.Height * $scale)
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.InterpolationMode = 'HighQualityBicubic'
    $g.DrawImage($img, 0, 0, $w, $h)
    $g.Dispose(); $img.Dispose()
    $bmp.Save($tmp, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
    $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($tmp)) ([Windows.Storage.StorageFile])
    $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $dec = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $sb = Await ($dec.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $res = Await ($engine.RecognizeAsync($sb)) ([Windows.Media.Ocr.OcrResult])
    $text = ($res.Lines | ForEach-Object { $_.Text }) -join "`n"
    $stream.Dispose(); $sb.Dispose()
    [IO.File]::WriteAllText($out, "SOURCE: $label`n" + $text)
  } catch {
    Add-Content (Join-Path $OutDir "_errors.log") "$path`t$($_.Exception.Message)"
  }
}
if (Test-Path $tmp) { Remove-Item $tmp }
