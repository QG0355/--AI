param(
  [Parameter(Mandatory = $true)]
  [string]$OutDir
)

$out = (Resolve-Path $OutDir).Path
$bundle = Join-Path $out 'GEMINI_CODE.md'

$paths = @(
  'it_backend\it_backend\settings.py',
  'it_backend\it_backend\urls.py',
  'it_backend\tickets_api\models.py',
  'it_backend\tickets_api\serializers.py',
  'it_backend\tickets_api\views.py',
  'it_backend\tickets_api\urls.py',
  'it_backend\tickets_api\admin.py',
  'it_backend\tickets_api\management\commands\ai_auto_review.py',
  'vite-project\src\router\index.js',
  'vite-project\src\stores\auth.js',
  'vite-project\src\views\AiAssistant.vue',
  'vite-project\src\views\SubmitTicket.vue',
  'vite-project\src\views\OAApproval.vue',
  'vite-project\src\views\Workplace.vue',
  'vite-project\src\views\MyTickets.vue'
)

Set-Content -Path $bundle -Value "# Code Bundle`n" -Encoding utf8

foreach ($p in $paths) {
  $full = Join-Path $out $p
  if (-not (Test-Path $full)) { continue }

  $ext = [IO.Path]::GetExtension($p).TrimStart('.')
  Add-Content -Path $bundle -Value ("---`n## $p`n" + '```' + $ext) -Encoding utf8
  (Get-Content -Path $full -Raw) | Add-Content -Path $bundle -Encoding utf8
  Add-Content -Path $bundle -Value '```' -Encoding utf8
}
