# Genera Memoria_EITI_Llanes.docx y .pdf a partir de memoria.md.
# Requiere pandoc y Microsoft Word. El formato sigue el Anexo II del reglamento.
# Uso: powershell -ExecutionPolicy Bypass -File build.ps1
$ErrorActionPreference = 'Stop'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $dir
# Word se cuelga al exportar el PDF dentro de esta carpeta, por eso se trabaja
# en una carpeta temporal y al final se copian los resultados.
$tmp = Join-Path $env:TEMP 'memoria_eiti_build'
if (-not (Test-Path $tmp)) { [void](New-Item -ItemType Directory $tmp) }
$docx = Join-Path $tmp 'm.docx'
$pdf = Join-Path $tmp 'm.pdf'
$titulo = 'Sistema de Gesti' + [char]0xF3 + 'n para Altacava Winebar'

pandoc memoria.md -f markdown -o $docx --resource-path=.
if ($LASTEXITCODE -ne 0) { throw 'pandoc fallo' }

function Cm([double]$cm) { return $cm * 28.3465 }

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$word.ScreenUpdating = $false
function Paso([string]$m) { Write-Output ((Get-Date -Format 'HH:mm:ss') + ' ' + $m) }
try {
    $doc = $word.Documents.Open($docx)
    $word.Options.CheckSpellingAsYouType = $false
    $word.Options.CheckGrammarAsYouType = $false
    Paso 'documento abierto'

    # Pagina: A4 y margenes del Anexo II
    $ps = $doc.PageSetup
    $ps.PaperSize = 7
    $ps.TopMargin = Cm 2.5; $ps.BottomMargin = Cm 2.5
    $ps.LeftMargin = Cm 3; $ps.RightMargin = Cm 3
    $ps.HeaderDistance = Cm 1.25; $ps.FooterDistance = Cm 1.25
    $ps.DifferentFirstPageHeaderFooter = -1

    # Estilos
    $nombres = @(-1, -2, -3, -4, 'Body Text', 'First Paragraph', 'Compact', 'Image Caption', 'Table Caption',
        'Captioned Figure', 'Portada', 'TituloSinNumero', 'Hyperlink', 'Verbatim Char')
    foreach ($n in $nombres) {
        try { $s = $doc.Styles.Item($n); $s.Font.Name = 'Times New Roman'; $s.Font.Color = 0 } catch {}
    }
    Paso 'estilos base'
    $normal = $doc.Styles.Item(-1)
    $normal.Font.Size = 12
    $normal.ParagraphFormat.SpaceAfter = 6
    $normal.ParagraphFormat.SpaceBefore = 0
    $normal.ParagraphFormat.LineSpacingRule = 0
    foreach ($n in 'Body Text', 'First Paragraph', 'Compact') {
        try {
            $s = $doc.Styles.Item($n)
            $s.Font.Size = 12
            $s.ParagraphFormat.Alignment = 3
            $s.ParagraphFormat.SpaceBefore = 0
            $s.ParagraphFormat.SpaceAfter = 6
            $s.ParagraphFormat.LineSpacingRule = 0
        } catch {}
    }
    $h = @{ -2 = 16; -3 = 14; -4 = 12 }
    foreach ($k in $h.Keys) {
        $s = $doc.Styles.Item($k)
        $s.Font.Size = $h[$k]; $s.Font.Bold = -1; $s.Font.Italic = 0
        $s.ParagraphFormat.SpaceBefore = 12; $s.ParagraphFormat.SpaceAfter = 6
        $s.ParagraphFormat.KeepWithNext = -1
    }
    $doc.Styles.Item(-2).ParagraphFormat.PageBreakBefore = -1
    $doc.Styles.Item(-2).ParagraphFormat.SpaceAfter = 12
    foreach ($n in 'Image Caption', 'Table Caption', 'Captioned Figure') {
        try {
            $s = $doc.Styles.Item($n)
            $s.Font.Size = 10; $s.Font.Italic = 0
            $s.ParagraphFormat.Alignment = 1
            $s.ParagraphFormat.SpaceAfter = 6
        } catch {}
    }
    try {
        $s = $doc.Styles.Item('Portada')
        $s.Font.Size = 16; $s.ParagraphFormat.Alignment = 1
        $s.ParagraphFormat.SpaceBefore = 12; $s.ParagraphFormat.SpaceAfter = 12
    } catch {}
    try {
        $s = $doc.Styles.Item('TituloSinNumero')
        $s.Font.Size = 16; $s.Font.Bold = -1; $s.ParagraphFormat.Alignment = 1
        $s.ParagraphFormat.SpaceAfter = 18
    } catch {}

    Paso 'estilos'
    # Tablas: centradas, con bordes y letra menor
    foreach ($t in $doc.Tables) {
        $t.Rows.Alignment = 1
        $t.Borders.Enable = -1
        $t.Range.Font.Size = 10
        $t.Range.ParagraphFormat.Alignment = 0
        $t.Range.ParagraphFormat.SpaceAfter = 2
    }

    Paso 'tablas'
    # Portada: se inserta al principio el documento "Portada Llanes.docx"
    $portada = Join-Path (Split-Path $dir -Parent) 'Portada Llanes.docx'
    if (Test-Path $portada) {
        $antes = $doc.Paragraphs.Count
        $doc.Range(0, 0).InsertFile($portada)
        $n = $doc.Paragraphs.Count - $antes
        # se quitan los parrafos vacios del final de la portada para que ocupe una sola pagina
        for ($i = $n; $i -ge 1; $i--) {
            $p = $doc.Paragraphs.Item($i)
            $vacio = ($p.Range.Text.Trim() -eq '') -and ($p.Range.InlineShapes.Count -eq 0) -and ($p.Range.ShapeRange.Count -eq 0)
            if (-not $vacio) { break }
            [void]$p.Range.Delete()
        }
        Paso 'portada insertada'
    } else {
        Write-Output "AVISO: no se encontro $portada; el documento queda sin portada."
    }

    # Encabezado (titulo) y pie (capitulo y numero de pagina)
    $h1 = $doc.Styles.Item(-2).NameLocal
    $sec = $doc.Sections.Item(1)
    $hdr = $sec.Headers.Item(1).Range
    $hdr.Text = $titulo
    $hdr.ParagraphFormat.Alignment = 1
    $hdr.Font.Size = 10; $hdr.Font.Name = 'Times New Roman'
    $ftr = $sec.Footers.Item(1)
    $r = $ftr.Range
    $r.Text = ''
    $r.Font.Size = 10; $r.Font.Name = 'Times New Roman'
    $estiloPie = $doc.Styles.Item(-33)
    $estiloPie.ParagraphFormat.TabStops.ClearAll()
    [void]$estiloPie.ParagraphFormat.TabStops.Add((Cm 15), 2)
    [void]$doc.Fields.Add($r, -1, "STYLEREF `"$h1`"", $false)
    $r = $ftr.Range; $r.InsertAfter("`t"); $r.Collapse(0)
    [void]$doc.Fields.Add($r, 33)

    Paso 'encabezado y pie'
    [void]$doc.Fields.Update()
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    [void]$doc.Fields.Update()

    Paso 'campos'
    $doc.Save()
    Write-Output ("Paginas: " + $doc.ComputeStatistics(2))
    $doc.Close($false)
} finally {
    $word.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
}
Copy-Item $docx (Join-Path $dir 'Memoria_EITI_Llanes.docx') -Force
Paso 'docx guardado'

# El PDF se exporta desde una copia, en otro proceso de PowerShell y con otra
# instancia de Word: exportarlo en la misma sesion en la que se aplico el
# formato deja a Word colgado.
$copia = Join-Path $tmp 'm_export.docx'
Copy-Item $docx $copia -Force
$exportar = @'
param($d, $p)
$w = New-Object -ComObject Word.Application
$w.DisplayAlerts = 0
$doc = $w.Documents.Open($d, $false, $true)
$doc.SaveAs2($p, 17)
$doc.Close($false)
$w.Quit()
'@
$ps1 = Join-Path $tmp 'exportar_pdf.ps1'
Set-Content $ps1 $exportar -Encoding ASCII
$job = Start-Job -FilePath $ps1 -ArgumentList $copia, $pdf
if (-not (Wait-Job $job -Timeout 90)) { Stop-Job $job; throw 'La exportacion a PDF no termino. El .docx si fue generado.' }
Receive-Job $job
Paso 'pdf exportado'

Copy-Item $pdf (Join-Path $dir 'Memoria_EITI_Llanes.pdf') -Force
Write-Output "Generado: Memoria_EITI_Llanes.docx y Memoria_EITI_Llanes.pdf"

