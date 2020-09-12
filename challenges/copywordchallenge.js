challengeDiv.textContent = '';
challengeDiv.style.lineHeight = "normal"
challengeDiv.style.marginTop = "3%"

var content = document.createTextNode("Type '{{WORD}}' into the box:");

var content_input = document.createElement('input');
content_input.style.width = "60%"
content_input.style.marginTop = "3%"
content_input.id = "noenter"

var btn = document.createElement('button');
btn.innerHTML = "Verify";
btn.type = "button"
btn.setAttribute("onClick","javascript: submit_challenge();")
btn.style.marginLeft = "15px"
		
challengeDiv.appendChild(content);
challengeDiv.appendChild(content_input);
challengeDiv.appendChild(btn);		

window.addEventListener('keydown',function(e){if(e.keyIdentifier=='U+000A'||e.keyIdentifier=='Enter'||e.keyCode==13){if(e.target.nodeName=='INPUT'&&e.target.type=='text'&&e.target.id=='noenter'){e.preventDefault();submit_challenge();return false;}}},true); // see https://stackoverflow.com/questions/5629805/disabling-enter-key-for-form/37241980


function submit_challenge(){
	
	// remove btn
	challengeDiv.removeChild(challengeDiv.children[1])
	
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
			
			challengeDiv.textContent = '';
			challengeDiv.style.marginTop = "0px"
			challengeDiv.style.marginLeft = "5px"
			challengeDiv.style.lineHeight = '75px'
				
		  if (httpRequest_challenge.status === 200) {
			  
			console.log(httpRequest_challenge.responseText);			
			
			res = JSON.parse(httpRequest_challenge.responseText);
			
			if (res['success']){				
				console.log('success')
				
				captcha_success(res['token'])
				
			} else {
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
	
	var params = 'challenge_id={{CHALLENGE_ID}}&answer=' + challengeDiv.children[0].value;

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