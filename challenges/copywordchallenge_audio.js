challengeDiv.textContent = '';
challengeDiv.style.lineHeight = "normal"
challengeDiv.style.marginTop = "3%"

var content_pre = document.createElement('span');
content_pre.textContent = 'Solve '
var content_audio = document.createElement('audio');
content_audio.src = '{{AUDIO}}'
content_audio.controls = 'controls';
content_audio.type = 'audio/mp3';
content_audio.style.width = '80%';
content_audio.style.height = '30%';

var content_input = document.createElement('input');
content_input.style.width = "60%"
content_input.style.marginTop = "3%"
content_input.id = "noenter"

var submit_challenge_btn = document.createElement('button');
submit_challenge_btn.innerHTML = "Verify";
submit_challenge_btn.type = "button"
submit_challenge_btn.setAttribute("onClick","javascript: submit_challenge();")
submit_challenge_btn.style.marginLeft = "15px"
		
challengeDiv.appendChild(content_pre);
challengeDiv.appendChild(content_audio);
challengeDiv.appendChild(content_input);
challengeDiv.appendChild(submit_challenge_btn);		



function submit_challenge(){
	
	// remove submit_challenge_btn
	challengeDiv.removeChild(challengeDiv.children[3])
	
	// disable input field
	content_input.disabled = true
	
	var loading = document.createElement('img');
	loading.style.verticalAlign = "middle"
	loading.src = loading_src
							
	challengeDiv.appendChild(loading);
	
	httpRequest_challenge = new XMLHttpRequest();
	
	httpRequest_challenge.onreadystatechange = function alertContents() {
		try {
		if (httpRequest_challenge.readyState === XMLHttpRequest.DONE) {
			
			clearTimeout(connection_issue_timeout)
			
			challengeDiv.textContent = '';
			challengeDiv.style.marginTop = "0px"
			challengeDiv.style.marginLeft = "5px"
			challengeDiv.style.lineHeight = '75px'
				
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
	
	var params = 'challenge_id={{CHALLENGE_ID}}&answer=' + challengeDiv.children[2].value;

	httpRequest_challenge.open('POST', '{{SITE_URL}}/solve', true);
	httpRequest_challenge.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	httpRequest_challenge.send(params);
	
	
	// set another timeout for 3 seconds, if still not ready, show connection issue
	// and offer to reload
	connection_issue_timeout_func()
	
}