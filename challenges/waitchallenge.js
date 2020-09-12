challengeDiv.textContent = 'Checking for bots...';

var loading = document.createElement('img');
loading.style.verticalAlign = "middle"
loading.src = loading_src
						
challengeDiv.appendChild(loading);

setTimeout(function(){
	
	httpRequest_challenge = new XMLHttpRequest();
	
	httpRequest_challenge.onreadystatechange = function alertContents() {
	  try {
		if (httpRequest_challenge.readyState === XMLHttpRequest.DONE) {
			challengeDiv.textContent = '';
			clearTimeout(connection_issue_timeout)
			
		  if (httpRequest_challenge.status === 200) {
			  
			console.log(httpRequest_challenge.responseText);			
			
			res = JSON.parse(httpRequest_challenge.responseText);
			
			if (res['success']){				
				console.log('success')
				captcha_success(res['token'])
			} else {
				console.log('FAIL challenge')
				captcha_fail()
			}
			
		  } else {
			captcha_submit_fail(httpRequest_challenge.status)
		  }
		}
	  }
	  catch( e ) {
		captcha_submit_fail(' exception, ' + e)
	  }
	}
	
	var params = 'challenge_id={{CHALLENGE_ID}}&answer=a';

	httpRequest_challenge.open('POST', '{{SITE_URL}}/solve', true);
	httpRequest_challenge.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	httpRequest_challenge.send(params);
	
	// set another timeout for 3 seconds, if still not ready, show connection issue
	// and offer to reload
	
	connection_issue_timeout_func()
	
}, 1000);