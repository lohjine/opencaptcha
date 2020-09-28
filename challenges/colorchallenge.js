challengeDiv.textContent = '';

const content = document.createTextNode("Are you a human?");

var btn = document.createElement('button');
btn.innerHTML = "Yes";
btn.type = "button"
btn.setAttribute("onClick","javascript: toggleModal();")
btn.style.marginLeft = "15px"
		
challengeDiv.appendChild(content);
challengeDiv.appendChild(btn);		

var challenge_images = {{IMAGES}}


var challenge_modal = document.createElement('div');
challenge_modal.className = "modal"
challenge_modal.style.position = "fixed"
challenge_modal.style.left = "0"
challenge_modal.style.top = "0"
challenge_modal.style.width = "100%"
challenge_modal.style.height = "100%"
challenge_modal.style.backgroundColor = "rgba(0,0,0,0.5)"
challenge_modal.style.opacity = "0"
challenge_modal.style.visibility = "hidden"
challenge_modal.style.transform = "scale(1.1)"
challenge_modal.style.transition = "visibility 0s linear 0.25s, opacity 0.25s 0s, transform 0.25s"
var challenge_modal_content = document.createElement('div');
challenge_modal_content.className = "modal-content"
challenge_modal_content.style.position = "absolute"
challenge_modal_content.style.top = "50%"
challenge_modal_content.style.left = "50%"
challenge_modal_content.style.transform = "translate(-50%, -50%)"
challenge_modal_content.style.backgroundColor = "white"
challenge_modal_content.style.padding = "1rem 1.5rem"
challenge_modal_content.style.width = "24rem"
challenge_modal_content.style.borderRadius = "0.5rem"
var challenge_close_button = document.createElement('span');
challenge_close_button.className = "close-button"
challenge_close_button.style.float = "right"
challenge_close_button.style.width = "1.5rem"
challenge_close_button.style.lineHeight = "1.5rem"
challenge_close_button.style.textAlign = "center"
challenge_close_button.style.cursor = "pointer"
challenge_close_button.style.borderRadius = "0.25rem"
challenge_close_button.style.backgroundColor = "lightgray"

// add the window

// fuck this shit


var challenge_text = document.createElement('span');
challenge_text.innerHTML = 'text'

challenge_modal_content.appendChild(challenge_close_button)
challenge_modal_content.appendChild(challenge_text)
challenge_modal.appendChild(challenge_modal_content)
challengeDiv.appendChild(challenge_modal)


var modal = document.querySelector(".modal");
var closeButton = document.querySelector(".close-button");

function toggleModal() {
        //modal.classList.toggle("show-modal");
		
		if (modal.style.opacity == 0){
			modal.style.opacity = "1"
			modal.style.visibility = "visible"
			modal.style.transform = "scale(1.0)"
			modal.style.transition = "visibility 0s linear 0s, opacity 0.25s 0s, transform 0.25s"
			
		} else {
			
			modal.style.opacity = "0"
			modal.style.visibility = "hidden"
			modal.style.transform = "scale(1.1)"
			modal.style.transition = "visibility 0s linear 0.25s, opacity 0.25s 0s, transform 0.25s"
			
		}
    }

function windowOnClick(event) {
	if (event.target === modal) {
		toggleModal();
	}
}

closeButton.addEventListener("click", toggleModal);
window.addEventListener("click", windowOnClick);


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
			  
			clearTimeout(connection_issue_timeout)
			
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
	
	var params = 'challenge_id={{CHALLENGE_ID}}&answer=a';

	httpRequest_challenge.open('POST', '{{SITE_URL}}/solve', true);
	httpRequest_challenge.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	httpRequest_challenge.send(params);
	
	
	// set another timeout for 3 seconds, if still not ready, show connection issue
	// and offer to reload
	
	connection_issue_timeout_func()
	
}