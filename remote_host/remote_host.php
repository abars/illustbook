<?php
header('content-type: application/json; charset=utf-8');

$hostname = gethostbyaddr($_SERVER['REMOTE_ADDR']);

print $_GET['callback'] . '("' . $hostname . '");';
?>