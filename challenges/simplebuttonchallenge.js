challengeDiv.textContent = '';

const content = document.createTextNode("Are you a human?");

var btn = document.createElement('button');
btn.innerHTML = "Yes";
btn.type = "button"
btn.setAttribute("onClick","javascript: submit_challenge();")
btn.style.marginLeft = "15px"
		
challengeDiv.appendChild(content);
challengeDiv.appendChild(btn);		


function submit_challenge(){
	
	// remove btn
	challengeDiv.removeChild(challengeDiv.children[0])
	
	var loading = document.createElement('img');
	loading.style.verticalAlign = "middle"
	loading.src = loading_src
							
	challengeDiv.appendChild(loading);
	
	httpRequest_challenge = new XMLHttpRequest();
	
	httpRequest_challenge.onreadystatechange = function alertContents() {
		try {
		if (httpRequest_challenge.readyState === XMLHttpRequest.DONE) {
			
			challengeDiv.textContent = '';
				
		  if (httpRequest_challenge.status === 200) {
			  
			console.log(httpRequest_challenge.responseText);			
			
			res = JSON.parse(httpRequest_challenge.responseText);
			
			if (res['success']){				
				console.log('success')
				
				
				var content = document.createTextNode("Verification successful");
				
				var tick = document.createElement('img');
				tick.style.verticalAlign = "middle"
				tick.src = tick_src
				
				challengeDiv.appendChild(tick);				
				challengeDiv.appendChild(content);
				
				// create the form with fields
				var opencaptcha_input = document.createElement('input');
				opencaptcha_input.type = 'hidden'
				opencaptcha_input.name = 'opencaptcha-response'
				opencaptcha_input.value = res['token']	
		
				challengeDiv.appendChild(opencaptcha_input);
				
			} else {
				console.log('FAIL challenge')
				
				var cross = document.createElement('img');
				cross.style.verticalAlign = "middle"
				cross.src = cross_src
				
				var content = document.createTextNode("Verification failed");
				
				challengeDiv.appendChild(cross);
				challengeDiv.appendChild(content);
				
				offer_reload()
			}
			
			
		  } else {
			  
			
			var cross = document.createElement('img');
			cross.style.verticalAlign = "middle"
			cross.src = cross_src
				
			var content = document.createTextNode("Submit captcha failed: " + httpRequest_challenge.status);
			
			challengeDiv.appendChild(cross);
			challengeDiv.appendChild(content);
			
			offer_reload()
		  }
		}
	  }
	  catch( e ) {
		  
		var cross = document.createElement('img');
		cross.style.verticalAlign = "middle"
		cross.src = cross_src
				
		challengeDiv.textContent = '';
		var content = document.createTextNode("Submit captcha failed, exception: " + e);
		
		challengeDiv.appendChild(cross);
		challengeDiv.appendChild(content);
		
		offer_reload()
	  }
	}
	
	var params = 'challenge_id={{CHALLENGE_ID}}&answer=a';

	httpRequest_challenge.open('POST', '{{SITE_URL}}/solve', true);
	httpRequest_challenge.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	httpRequest_challenge.send(params);
	
	
	// set another timeout for 3 seconds, if still not ready, show connection issue
	// and offer to reload
	
	setTimeout(function(){
		if (httpRequest_challenge.readyState === XMLHttpRequest.DONE) {
			
		} else {
			offer_reload()
		}
	}, 3000);
	
}