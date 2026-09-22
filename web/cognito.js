// Cognito sign-up, confirm, and login from the browser.
// Local laptop: COGNITO_CLIENT_ID is empty, so this is skipped.

function cognitoIsOn() {
  return Boolean(window.COGNITO_CLIENT_ID);
}

function cognitoUrl() {
  return "https://cognito-idp." + window.COGNITO_REGION + ".amazonaws.com/";
}

function getIdToken() {
  return sessionStorage.getItem("idToken") || "";
}

function setIdToken(token) {
  if (token) {
    sessionStorage.setItem("idToken", token);
  } else {
    sessionStorage.removeItem("idToken");
  }
}

function cognitoCall(target, payload) {
  return fetch(cognitoUrl(), {
    method: "POST",
    headers: {
      "Content-Type": "application/x-amz-json-1.1",
      "X-Amz-Target": target,
    },
    body: JSON.stringify(payload),
  }).then(function (response) {
    return response.json().then(function (data) {
      return { ok: response.ok, data: data };
    });
  });
}

function cognitoMessage(data, fallback) {
  if (data && data.message) {
    return data.message;
  }
  return fallback;
}

function cognitoSignUp(email, password) {
  return cognitoCall("AWSCognitoIdentityProviderService.SignUp", {
    ClientId: window.COGNITO_CLIENT_ID,
    Username: email,
    Password: password,
    UserAttributes: [{ Name: "email", Value: email }],
  });
}

function cognitoConfirm(email, code) {
  return cognitoCall("AWSCognitoIdentityProviderService.ConfirmSignUp", {
    ClientId: window.COGNITO_CLIENT_ID,
    Username: email,
    ConfirmationCode: code,
  });
}

function cognitoLogin(email, password) {
  return cognitoCall("AWSCognitoIdentityProviderService.InitiateAuth", {
    AuthFlow: "USER_PASSWORD_AUTH",
    ClientId: window.COGNITO_CLIENT_ID,
    AuthParameters: {
      USERNAME: email,
      PASSWORD: password,
    },
  }).then(function (result) {
    if (!result.ok) {
      return result;
    }
    var auth = result.data.AuthenticationResult || {};
    if (!auth.IdToken) {
      return { ok: false, data: { message: "Login did not return a token." } };
    }
    setIdToken(auth.IdToken);
    return result;
  });
}
