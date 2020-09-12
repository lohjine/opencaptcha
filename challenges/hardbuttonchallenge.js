challengeDiv.textContent = '';

const content = document.createTextNode("Are you a human?");

var btn = document.createElement('button');
btn.innerHTML = "Yes";
btn.type = "button"
btn.setAttribute("onClick","javascript: submit_challenge('{{RIGHT}}');")
btn.style.marginLeft = "15px"
		
var btn2 = document.createElement('button');
btn2.innerHTML = "No";
btn2.type = "button"
btn2.setAttribute("onClick","javascript: submit_challenge('{{WRONG}}');")
btn2.style.marginLeft = "15px"

challengeDiv.appendChild(content);
if (Math.random() > 0.5){
challengeDiv.appendChild(btn);
challengeDiv.appendChild(btn2);
} else {
challengeDiv.appendChild(btn2);
challengeDiv.appendChild(btn);
}		


function submit_challenge(answer){
	
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
				
				
				captcha_success(token)
				
				
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
	
	var params = 'challenge_id={{CHALLENGE_ID}}&answer=' + answer;

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