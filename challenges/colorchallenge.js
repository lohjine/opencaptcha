offer_audio()

challengeDiv.textContent = '';

var content = document.createTextNode("Are you a human?");

var btn = document.createElement('button');
btn.innerHTML = "Yes";
btn.type = "button"
btn.setAttribute("onClick","javascript: toggleModal();")
btn.style.marginLeft = "15px"
		
challengeDiv.appendChild(content);
challengeDiv.appendChild(btn);		

var challenge_images = {{IMAGES}}
var challenge_image_directory = {{IMAGE_DIR}}


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
challenge_modal.style.lineHeight = "1em"
var challenge_modal_content = document.createElement('div');
challenge_modal_content.className = "modal-content"
challenge_modal_content.style.position = "absolute"
challenge_modal_content.style.top = "50%"
challenge_modal_content.style.left = "50%"
challenge_modal_content.style.transform = "translate(-50%, -50%)"
challenge_modal_content.style.backgroundColor = "white"
challenge_modal_content.style.padding = "1rem 1.5rem"
challenge_modal_content.style.width = "400px"
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
challenge_close_button.innerHTML = '&times;'

// Setup the captcha window
var challenge_text = document.createElement('h2');
challenge_text.innerHTML = 'Select the 3 images that have normal colors.'
challenge_text.style.lineHeight= "1em"

// create the grid
var images_grid = document.createElement('div');
images_grid.style.display = "grid"
images_grid.style.gridTemplateColumns = "126px 126px 126px"
images_grid.style.gridGap = "10px"


var images = []

for (i = 0; i < 9; i++) { 
	images = images.concat(document.createElement('div'))
}


function togglechoice(ele){
	
	if (ele.style.BoxShadow == "") {	
		ele.style.webkitBoxShadow = "inset 0px 0px 0px 5px #f00";
		ele.style.mozBoxShadow = "inset 0px 0px 0px 5px #f00";
		ele.style.BoxShadow = "inset 0px 0px 0px 5px #f00";
	} else {
		ele.style.webkitBoxShadow = "";
		ele.style.mozBoxShadow = "";
		ele.style.BoxShadow = "";
	}
	
}

for (i = 0, l = images.length; i < l; i++){
	
	
	images[i].style.backgroundImage = "url(/challenges/image/" +  challenge_images[i] + "?directory=" + challenge_image_directory + ")"
	images[i].style.width = '126px'
	images[i].style.height = '126px'
	images[i].onclick = function(){togglechoice(this)}
	images[i].style.BoxShadow = "";
	
	
	images_grid.appendChild(images[i])
}


//create the bottom section
var challenge_bottom_panel = document.createElement('div');
challenge_bottom_panel.style.marginTop = "10px"

var submit_challenge_btn = document.createElement('button');
submit_challenge_btn.innerHTML = "Submit";
submit_challenge_btn.type = "button"
submit_challenge_btn.setAttribute("onClick","javascript: submit_challenge();")
submit_challenge_btn.style.float = "right";
submit_challenge_btn.style.height = "2.5em";
submit_challenge_btn.style.width = "6em";
submit_challenge_btn.style.fontSize = "large";

challenge_bottom_panel.appendChild(submit_challenge_btn)

challenge_modal_content.appendChild(challenge_close_button)
challenge_modal_content.appendChild(challenge_text)
challenge_modal_content.appendChild(images_grid)
challenge_modal_content.appendChild(challenge_bottom_panel)

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
	
	toggleModal()
	
	// prep answers
	var answer = []
	for (i = 0, l = images.length; i < l; i++){
		if (!(images[i].style.BoxShadow == "")){
			answer = answer.concat(i)
		}
	}
	answer = answer.toString()
	
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
	
	var params = 'challenge_id={{CHALLENGE_ID}}&answer=' + answer;

	httpRequest_challenge.open('POST', '{{SITE_URL}}/solve', true);
	httpRequest_challenge.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	httpRequest_challenge.send(params);
	
	
	// set another timeout for 3 seconds, if still not ready, show connection issue
	// and offer to reload
	
	connection_issue_timeout_func()
	
}