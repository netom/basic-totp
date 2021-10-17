<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Please Log In</title>

<style type="text/css">
html {
    font-family: Helvetica, Arial, sans-serif;
    font-weight: 400;
}

h1 {
    margin: 5em 0em 2em 0em;
    text-align: center;
    font-weight: 400;
}

.form {
    margin: auto;
    max-width: 20em;
    border: 1px solid #cccccc;
    border-radius: 0.2em;
    padding: 1em;
}

.form .row input {
    width: 97%;
    margin: 0.2em 0em 0.9em 0em;
    border: 1px solid #cccccc;
    font-size: 1em;
}

input[type=submit] {
    font-size: 1.1em;
    border: 1px solid #006bb4;
    padding: 0.4em 1.5em 0.4em 1.5em;
    border-radius: 0.2em;
    background-color: #006bb4;
    color: #ffffff;
}

</style>

</head>
<body>
<h1>Protected Area</h1>

<form action="/auth/login" method="POST" class="form">

<div class="row"><label for="username">Username:</label></div>
<div class="row"><input type="text" name="username"></div>

<div class="row"><label for="password">Password:</label></div>
<div class="row"><input type="password" name="password"></div>

<div class="row"><label for="totp">Token:</label></div>
<div class="row"><input type="text" name="totp"></div>

<div><input type="submit" value="Log in"></div>

</form>

</body>
</html>