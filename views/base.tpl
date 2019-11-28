% from application import __VERSION__
<!DOCTYPE html>
<head>
<title>pass.sh</title>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8">
<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css?family=Fira+Code:400,500|VT323&display=swap" rel="stylesheet">

<!-- UIkit CSS -->
<link rel="stylesheet" href="/static/uikit.min.css" />
<link rel="stylesheet" href="/static/style.css" />
<link rel="icon" type="image/png" href="/static/favicon.ico">
<!-- UIkit JS -->
<script src="/static/uikit.min.js"></script>
<script src="/static/uikit-icons.min.js"></script>

</head>
<body>
<div class="uk-container uk-container-small">
<div id="header" class="uk-card uk-card-default uk-card-body custom">
  <h3 class="uk-card-title"><a href="/" style="font-family: 'VT323', monospace; font-size: 32px; text-decoration: none; padding-left:6px; padding-right:6px; color:#000; background-color:#fff; border:1px solid #b7d9fa; border-radius:4px 0px 0px 4px;">PASS.SH</a><span style="border-bottom: 1px solid #b7d9fa; border-top: 1px solid #b7d9fa; border-bottom: 1px solid #b7d9fa; border-radius:0px 4px 4px 0px; padding-right:6px; text-align:right; padding-left:6px; background-color:#1e87f0; color:#fff; font-family: 'VT323', monospace; font-size: 32px;">***</span></h3>
</div>
</div>
<div class="uk-container uk-container-small">
{{!base}}
</div>
<div class="uk-container uk-container-small uk-text-center uk-margin-small-top" style="background-color: #f2f2f2; border-radius:5px; padding:4px;">
<a href="https://github.com/jadacyrus/pass.sh" target="_blank" class="uk-link-text">
  <span uk-icon="icon: github-alt" class="uk-icon">
  <span class="uk-text-middle">check out my code here!</span>
</a>
  <span class="uk-text-middle uk-text-small uk-text-muted">version: {{ __VERSION__ }}</span>
</div>
</body>
</html>
