// get the div 
q = document.getElementsByClassName('opencaptcha')[0]
sitekey = q.attributes['data-sitekey'].value

// edit style
q.style.width = "300px"
q.style.height = "75px"
q.style.background = "#f9f9f9"
q.style.border = "1px solid #d3d3d3"
q.style.color = "#000"

// create challenge space and logo space
const challengeDiv = document.createElement("div"); 
challengeDiv.style.width = "calc(80% - 5px)" 
challengeDiv.style.float = "left"
  
const logoDiv = document.createElement("div"); 
logoDiv.style.width = "20%" 
logoDiv.style.float = "right"
logoDiv.style.textAlign = "center"
logoDiv.style.marginTop = "15px"

const linkCap = document.createElement("a"); 
linkCap.textContent = 'Open\nCaptcha'
linkCap.href = "https://opencaptcha.lohjine.com"
linkCap.target = "_blank"
linkCap.style.color = "black"
linkCap.style.textDecoration = "none"
linkCap.style.display = "block"

logoDiv.appendChild(linkCap)

q.appendChild(challengeDiv);
q.appendChild(logoDiv);

// query server with details

var reload_btn = document.createElement('button');
reload_btn.innerHTML = "Reload Captcha"
reload_btn.style.display = "none"
reload_btn.style.marginLeft = "-6px"
reload_btn.type = "button"
reload_btn.setAttribute("onClick","javascript: load_captcha();")
logoDiv.appendChild(reload_btn);	
	
function offer_reload(){
	// replace opencaptcha logo with reload button?
	// or just shift up
	linkCap.style.display = "none"
	reload_btn.style.display = "block";
	
	if (logoDiv.childElementCount > 2){
		logoDiv.removeChild(logoDiv.children[2]) 
	}
}

function offer_audio(){
	var audio_challenge = document.createElement('button');
	audio_challenge.type = 'button'
	audio_challenge.title = "Switch to Audio Captcha"
	audio_challenge.style.backgroundImage = "url(" + audio_src + ")"
	audio_challenge.style.height = "25px"
	audio_challenge.style.width = "25px"
	audio_challenge.style.backgroundSize = "100% 100%"
	audio_challenge.setAttribute("onClick","javascript: load_captcha(true);")

	logoDiv.appendChild(audio_challenge)
	
}

function load_captcha(audio=false){
	linkCap.style.display = "block"
	reload_btn.style.display = "none";
	
	challengeDiv.style.marginTop = "0px"
	challengeDiv.style.marginLeft = "5px"
	challengeDiv.style.lineHeight = '75px'
	challengeDiv.textContent = "Loading Captcha..."
	
	httpRequest = new XMLHttpRequest();

	httpRequest.onreadystatechange = function alertContents() {
	  try {
		if (httpRequest.readyState === XMLHttpRequest.DONE) {
		  if (httpRequest.status === 200) {
			  
			
			// display the challenge				
			var content = document.createTextNode("Load complete");
			challengeDiv.appendChild(content);
			
			var s = document.createElement("script");
			s.text = httpRequest.responseText;

			// add challenge to body and run
			document.body.appendChild(s);
			
		  } else {
			  
			challengeDiv.textContent = '';
				
			var content = document.createTextNode("Loading captcha failed: " + httpRequest.status);
			challengeDiv.appendChild(content);
			
			offer_reload()
		  }
		}
	  }
	  catch( e ) {
		challengeDiv.textContent = '';
		
		var content = document.createTextNode("Loading captcha failed, exception: " + e);
		challengeDiv.appendChild(content);
		
		offer_reload()
	  }
	}
	httpRequest.open('POST', '{{SITE_URL}}/request', true);
	httpRequest.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	
	if (audio){
		params = 'site_key=' + sitekey + '&blind=true';
		logoDiv.removeChild(logoDiv.children[2]) // remove audio button
	} else {
		params = 'site_key=' + sitekey;
	}
	
	httpRequest.send(params);
	
}

function captcha_success(token){
	
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
	
}

function captcha_fail(){
	
	var cross = document.createElement('img');
	cross.style.verticalAlign = "middle"
	cross.src = cross_src
	
	var content = document.createTextNode("Verification failed");
	
	challengeDiv.appendChild(cross);
	challengeDiv.appendChild(content);
	
	offer_reload()
}

function captcha_submit_fail(error){
	var cross = document.createElement('img');
	cross.style.verticalAlign = "middle"
	cross.src = cross_src
		
	challengeDiv.textContent = '';
	var content = document.createTextNode("Submit captcha failed: " + error);
	
	challengeDiv.appendChild(cross);
	challengeDiv.appendChild(content);
	
	offer_reload()
}

const tick_src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/wD/AP+gvaeTAAAFJUlEQVRoge2ZXVCUVRzGn3cXFlkUdQFxWR1n+tLGGaYZmboNsjLTxo+E1OxLTRh0aqy7ppm3semuCwss/GCw0UmBUjOZaQomL0PIujBCSVMgxwLEQIh33/N/ulhA2V32fZddFmfkf8NyZs85v+f8n3POnnOA6ZiO+zu0eDRSzWpnj7nocXEgH8JlQi4h6SVlppCgxn5S/hJBKyDNytQaBtPPNuqaLlMqoJKNC03RSkm+LKCPJIQESZAS+IzA/3fKCYGAlA4FHjH9qlzPWNmRUAGV/DlLCT8k5DWSLgmBtIIfU2YoTSrhUO/r6au7Jl3AQZ7fRPJTUnkCQDHBj9YHpVsJdu7JWnVsUgRUsCnZCcc+kttIQTzhR+uREEFF17zru/ZrO/xxE1DBJncSHLVCPjeZ8KPlwroZkrRBz1k9YMXmsDPyCYUPtLPyNoZO6ReqXTELcMKxL6HwJIQCgsv75mp7rfgiWugQz28WypGEw9/dF+Slvb6Nx6MWcJg/ZRhM+p2UzKmCH26jJ9nJxR/nbAq7xI5rIUOSProH4EGKZ8iQD6LKwAH+uoBi/BGHTSpW+JFJbfhNPrz/wVeu2coAxdiZKHjTNNDWfAGDA4Nh4QWEkC6HgyW2MqCTDq86d1XABZMN7zf9aDh8EtcuXMLsLA+e2VGElFluBC8aJCHCzpsPuBfVaIUqYgbmm41PJALeNA3UV51Ae0sbAODW392oP1ATHj7Qty/9yr/LLC0kDuQnAv6HqpPoaL0cat+wc2G0r4Lg7yeFNCCSR2JybfPFNyHw6VkePLl1XSR4kLDOAMlH7MAP3B7Ab+d+gen3T9g2IzEnOwNPF2+Aa1ZqBHhCwMXWGSC8lvB9/Tj+ySF0dd7AokcfwqrtG+FwOic88gVb1yM5zQI+8NdrIwPDx8AItqktq0JX5w0AwNWWNpw5cAzKb0xo5Jdvf9F65EfaBWdZCrDl+aA6f7ZcwplD1VBmsJ3Gn7BzsjNQ8MY6JKfNsAsPMrjncBkA+60m7NqSLcjMmTem3tWWNtQdrIZ/WMSIberD2SbTg/zX10YFLySE0mdDgFy3Wm1SZrqxpvRVZASJaG+9jO8qa2H6zWHPnwqxTXqmB09tWwfXTNu2uXtnvm4tQHDRzlI5Iy0VL5Rsgcc7VkRH62V8X/VVBM+vnyg8FNFqJwNNdtf5gIhN8HizQkTEyzajOzMJUJosBShTa4hmk3KlufF8caiIYPgYbDNabkIaLAUMpp9tpLA9mh02xZ2KFW8WYa43c9LgBbyWu7S32VKArumiNDlqFz7QiSDFnYpntxdi7vw7IuIIDxBHw11Fhj0PmH5VTtKI9jDicqdi+dYN8Piy4fFlxzRhZWxfQ5pS5eFYxz0T6711n0FQHMtJKvIPM9vwIKXs69zdu8Jxjn+tojneI6XrHoDv9kc4E48rQJ+9okcEu6YYHgRLTue9O+6lb8SLrT1Zq46JoGKq4JWw/ETuOzWRGC1v5i7N+69UyJMJhwfO3LrZ97YVn6WAGq1QpaqkzUKpSxS8kN+KkVb4Y75uxiwAAPSc1QO35nevIfB5ImzT29O39nTeDsubaWACDxxvdX5ZREFZ8K1dHOD/IVhq5fngsJWBu2Ovb+NxpRlLKNwn4FA8NilSypxOLIkWHojxka+4/bAPJnYKuZnkwmjgFdCukUc0pcprHtvdOVGGuDyz6tQd7VcW5JEsoGCZgIsp9BEMnK+p+kl0KOIiKE0mpCF3aW9zPJ5Zp2M67vf4H0ApRBRylukUAAAAAElFTkSuQmCC"

const cross_src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/wD/AP+gvaeTAAAEi0lEQVRoge2ZTU8bVxSG33NpU5WCKCUTY4TUWBDCh+hiZmE2LMKCOwKFIqxIbQqb/ICA2k35B+2qVf9D1aZVUkWVgqgrpQsWYVEWVIaqRsIIRIlg4YliyxH4nC74ECB7fMdjFpX8Sl5Yc+fc9xnfc+fcY6Cuuuqq63+j3PRUVB5MNF9VfHkw0ZybnooGuUeZDizMJB4qUtuFw2ub+ZlEPLg9f+VnEvHC4bVNRWq7MH1v1vQ+Mgr+2dQcBN+cfhfIKyLSjd8/eVGN2cvK3Z90CA1JQFrPjAnNv/vD468q3VsRIP/p5JycM39Or0iUbnwUDiJ3f9IBIwmg9fI1EZpvevSLL4QvwOt7E7MgfOszxFOKdOOPT5fN7F5U/pOP48yyCKCl3BgBzTb/9PS7ctfLAuSmdJTV29sAGvxtkMdS1C2PnwWC8BJjcUUNi4CUNX+iIhF3Nv38bK/UxbJJnD9657VwMSvM8P8UW0iw6CXGjBPbS4zFSbAoXGwxiJ/NI/+6XCzfJZSd0jYxJQF8YOILityWJwu+OZGdHHUIquSaryZmxSTO3tU2IMYQBHZbfv295ITZ8VEHqnTCBo11KqNtNHtX28JsDMEsbtvCxYmz46OOHD8II/OlYpSSEQAAZPWIzcp8OQnozEB2/I7DfHGfN723kowBAGBfj9gqwHKCEpeLdKjIfNlAidu28IfxuyUQAAAcjN6JQ9h3775g6FhmY0np6789D7QdBwYAgP2RYRvHT9XklzCRRyz6+vOlwC/EqgCAYwgWTlJoCPIY0O1VmAdCAADA/vCQzWSc2KXkCYtuX3pRlXkgJAAA7A4P2UqME/u8PIBCmQdqAAAAu0OOTUoFgfBIsW5f+jOUeQB4K2wAAIAIMYMAMRpOAIpFqcnDC7+E4rbDYrzPn5cHgtu5vBLqPBEKYMu2HdXASUhg86fyiJXbuVI9RNUAW/agQ0LVPPnL8hTB7VxZrQqiKoCtwUEHyrgwM5HHotzYanCIwACbH/XHScjkJAWATkoJs7FComOra1dXSmwN9jpc5gBeQh5EaRI5FBWgAGRyY+vrtS/mNnp7HUVsfhgh0bG19DIAZPq6bYbxe8IjsBtb36hdOb3R2xUkYT3FpGPp9IWlkO7rthUbF4CeUjCCqAiw0dXloAGmW6XHULrnkvlTpbu7bRCSBDE7FAm5tzb8IXwBNrq6HBHzZSMsuieT8U3CdPeHNth8OYHFvZXJBD/U/337drN6U9gE0GY0Eaii+VP9c/NmHPBvaJ1JcHDYlI8NpPZLtlbK9oW4UGgS5vcr923Yw1HR2DwA9GQyyzgqamH2KsYXbkXuvaZyscoC9G9t/Sssn1cyTyy6Z2cncFXZs7OzTCwGEPLFQCZTsisHGCTxWjQ6R1SquUseq6Ie2HkZqiRe6+iwqWyjgOb7dnerb+6eTRKNXGivA/BEoAdehjN/Fr+jwwYXL0HQl/17e1/XIv7xJJY1m7Kso5Rl7acikZr/wZGKROIpyzo4meNhreMDAP66cSOSsqyyCRVWKctqSllW+1XFr6uuuuqqvf4DtHiJ42XrW+MAAAAASUVORK5CYII="

const loading_src = "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4KPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBzdHlsZT0ibWFyZ2luOiBhdXRvOyBiYWNrZ3JvdW5kOiByZ2JhKDAsIDAsIDAsIDApIG5vbmUgcmVwZWF0IHNjcm9sbCAwJSAwJTsgZGlzcGxheTogYmxvY2s7IHNoYXBlLXJlbmRlcmluZzogYXV0bzsiIHdpZHRoPSI0MnB4IiBoZWlnaHQ9IjQycHgiIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJ4TWlkWU1pZCI+CjxnIHRyYW5zZm9ybT0icm90YXRlKDAgNTAgNTApIj4KICA8cmVjdCB4PSI0NyIgeT0iMjQiIHJ4PSIzIiByeT0iNiIgd2lkdGg9IjYiIGhlaWdodD0iMTIiIGZpbGw9IiMwMDAwMDAiPgogICAgPGFuaW1hdGUgYXR0cmlidXRlTmFtZT0ib3BhY2l0eSIgdmFsdWVzPSIxOzAiIGtleVRpbWVzPSIwOzEiIGR1cj0iMXMiIGJlZ2luPSItMC45MTY2NjY2NjY2NjY2NjY2cyIgcmVwZWF0Q291bnQ9ImluZGVmaW5pdGUiPjwvYW5pbWF0ZT4KICA8L3JlY3Q+CjwvZz48ZyB0cmFuc2Zvcm09InJvdGF0ZSgzMCA1MCA1MCkiPgogIDxyZWN0IHg9IjQ3IiB5PSIyNCIgcng9IjMiIHJ5PSI2IiB3aWR0aD0iNiIgaGVpZ2h0PSIxMiIgZmlsbD0iIzAwMDAwMCI+CiAgICA8YW5pbWF0ZSBhdHRyaWJ1dGVOYW1lPSJvcGFjaXR5IiB2YWx1ZXM9IjE7MCIga2V5VGltZXM9IjA7MSIgZHVyPSIxcyIgYmVnaW49Ii0wLjgzMzMzMzMzMzMzMzMzMzRzIiByZXBlYXRDb3VudD0iaW5kZWZpbml0ZSI+PC9hbmltYXRlPgogIDwvcmVjdD4KPC9nPjxnIHRyYW5zZm9ybT0icm90YXRlKDYwIDUwIDUwKSI+CiAgPHJlY3QgeD0iNDciIHk9IjI0IiByeD0iMyIgcnk9IjYiIHdpZHRoPSI2IiBoZWlnaHQ9IjEyIiBmaWxsPSIjMDAwMDAwIj4KICAgIDxhbmltYXRlIGF0dHJpYnV0ZU5hbWU9Im9wYWNpdHkiIHZhbHVlcz0iMTswIiBrZXlUaW1lcz0iMDsxIiBkdXI9IjFzIiBiZWdpbj0iLTAuNzVzIiByZXBlYXRDb3VudD0iaW5kZWZpbml0ZSI+PC9hbmltYXRlPgogIDwvcmVjdD4KPC9nPjxnIHRyYW5zZm9ybT0icm90YXRlKDkwIDUwIDUwKSI+CiAgPHJlY3QgeD0iNDciIHk9IjI0IiByeD0iMyIgcnk9IjYiIHdpZHRoPSI2IiBoZWlnaHQ9IjEyIiBmaWxsPSIjMDAwMDAwIj4KICAgIDxhbmltYXRlIGF0dHJpYnV0ZU5hbWU9Im9wYWNpdHkiIHZhbHVlcz0iMTswIiBrZXlUaW1lcz0iMDsxIiBkdXI9IjFzIiBiZWdpbj0iLTAuNjY2NjY2NjY2NjY2NjY2NnMiIHJlcGVhdENvdW50PSJpbmRlZmluaXRlIj48L2FuaW1hdGU+CiAgPC9yZWN0Pgo8L2c+PGcgdHJhbnNmb3JtPSJyb3RhdGUoMTIwIDUwIDUwKSI+CiAgPHJlY3QgeD0iNDciIHk9IjI0IiByeD0iMyIgcnk9IjYiIHdpZHRoPSI2IiBoZWlnaHQ9IjEyIiBmaWxsPSIjMDAwMDAwIj4KICAgIDxhbmltYXRlIGF0dHJpYnV0ZU5hbWU9Im9wYWNpdHkiIHZhbHVlcz0iMTswIiBrZXlUaW1lcz0iMDsxIiBkdXI9IjFzIiBiZWdpbj0iLTAuNTgzMzMzMzMzMzMzMzMzNHMiIHJlcGVhdENvdW50PSJpbmRlZmluaXRlIj48L2FuaW1hdGU+CiAgPC9yZWN0Pgo8L2c+PGcgdHJhbnNmb3JtPSJyb3RhdGUoMTUwIDUwIDUwKSI+CiAgPHJlY3QgeD0iNDciIHk9IjI0IiByeD0iMyIgcnk9IjYiIHdpZHRoPSI2IiBoZWlnaHQ9IjEyIiBmaWxsPSIjMDAwMDAwIj4KICAgIDxhbmltYXRlIGF0dHJpYnV0ZU5hbWU9Im9wYWNpdHkiIHZhbHVlcz0iMTswIiBrZXlUaW1lcz0iMDsxIiBkdXI9IjFzIiBiZWdpbj0iLTAuNXMiIHJlcGVhdENvdW50PSJpbmRlZmluaXRlIj48L2FuaW1hdGU+CiAgPC9yZWN0Pgo8L2c+PGcgdHJhbnNmb3JtPSJyb3RhdGUoMTgwIDUwIDUwKSI+CiAgPHJlY3QgeD0iNDciIHk9IjI0IiByeD0iMyIgcnk9IjYiIHdpZHRoPSI2IiBoZWlnaHQ9IjEyIiBmaWxsPSIjMDAwMDAwIj4KICAgIDxhbmltYXRlIGF0dHJpYnV0ZU5hbWU9Im9wYWNpdHkiIHZhbHVlcz0iMTswIiBrZXlUaW1lcz0iMDsxIiBkdXI9IjFzIiBiZWdpbj0iLTAuNDE2NjY2NjY2NjY2NjY2N3MiIHJlcGVhdENvdW50PSJpbmRlZmluaXRlIj48L2FuaW1hdGU+CiAgPC9yZWN0Pgo8L2c+PGcgdHJhbnNmb3JtPSJyb3RhdGUoMjEwIDUwIDUwKSI+CiAgPHJlY3QgeD0iNDciIHk9IjI0IiByeD0iMyIgcnk9IjYiIHdpZHRoPSI2IiBoZWlnaHQ9IjEyIiBmaWxsPSIjMDAwMDAwIj4KICAgIDxhbmltYXRlIGF0dHJpYnV0ZU5hbWU9Im9wYWNpdHkiIHZhbHVlcz0iMTswIiBrZXlUaW1lcz0iMDsxIiBkdXI9IjFzIiBiZWdpbj0iLTAuMzMzMzMzMzMzMzMzMzMzM3MiIHJlcGVhdENvdW50PSJpbmRlZmluaXRlIj48L2FuaW1hdGU+CiAgPC9yZWN0Pgo8L2c+PGcgdHJhbnNmb3JtPSJyb3RhdGUoMjQwIDUwIDUwKSI+CiAgPHJlY3QgeD0iNDciIHk9IjI0IiByeD0iMyIgcnk9IjYiIHdpZHRoPSI2IiBoZWlnaHQ9IjEyIiBmaWxsPSIjMDAwMDAwIj4KICAgIDxhbmltYXRlIGF0dHJpYnV0ZU5hbWU9Im9wYWNpdHkiIHZhbHVlcz0iMTswIiBrZXlUaW1lcz0iMDsxIiBkdXI9IjFzIiBiZWdpbj0iLTAuMjVzIiByZXBlYXRDb3VudD0iaW5kZWZpbml0ZSI+PC9hbmltYXRlPgogIDwvcmVjdD4KPC9nPjxnIHRyYW5zZm9ybT0icm90YXRlKDI3MCA1MCA1MCkiPgogIDxyZWN0IHg9IjQ3IiB5PSIyNCIgcng9IjMiIHJ5PSI2IiB3aWR0aD0iNiIgaGVpZ2h0PSIxMiIgZmlsbD0iIzAwMDAwMCI+CiAgICA8YW5pbWF0ZSBhdHRyaWJ1dGVOYW1lPSJvcGFjaXR5IiB2YWx1ZXM9IjE7MCIga2V5VGltZXM9IjA7MSIgZHVyPSIxcyIgYmVnaW49Ii0wLjE2NjY2NjY2NjY2NjY2NjY2cyIgcmVwZWF0Q291bnQ9ImluZGVmaW5pdGUiPjwvYW5pbWF0ZT4KICA8L3JlY3Q+CjwvZz48ZyB0cmFuc2Zvcm09InJvdGF0ZSgzMDAgNTAgNTApIj4KICA8cmVjdCB4PSI0NyIgeT0iMjQiIHJ4PSIzIiByeT0iNiIgd2lkdGg9IjYiIGhlaWdodD0iMTIiIGZpbGw9IiMwMDAwMDAiPgogICAgPGFuaW1hdGUgYXR0cmlidXRlTmFtZT0ib3BhY2l0eSIgdmFsdWVzPSIxOzAiIGtleVRpbWVzPSIwOzEiIGR1cj0iMXMiIGJlZ2luPSItMC4wODMzMzMzMzMzMzMzMzMzM3MiIHJlcGVhdENvdW50PSJpbmRlZmluaXRlIj48L2FuaW1hdGU+CiAgPC9yZWN0Pgo8L2c+PGcgdHJhbnNmb3JtPSJyb3RhdGUoMzMwIDUwIDUwKSI+CiAgPHJlY3QgeD0iNDciIHk9IjI0IiByeD0iMyIgcnk9IjYiIHdpZHRoPSI2IiBoZWlnaHQ9IjEyIiBmaWxsPSIjMDAwMDAwIj4KICAgIDxhbmltYXRlIGF0dHJpYnV0ZU5hbWU9Im9wYWNpdHkiIHZhbHVlcz0iMTswIiBrZXlUaW1lcz0iMDsxIiBkdXI9IjFzIiBiZWdpbj0iMHMiIHJlcGVhdENvdW50PSJpbmRlZmluaXRlIj48L2FuaW1hdGU+CiAgPC9yZWN0Pgo8L2c+CjwhLS0gW2xkaW9dIGdlbmVyYXRlZCBieSBodHRwczovL2xvYWRpbmcuaW8vIC0tPjwvc3ZnPg=="


const audio_src = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+Cgk8c3R5bGU+CgkJdHNwYW4geyB3aGl0ZS1zcGFjZTpwcmUgfQoJCS5zaHAwIHsgZmlsbDogIzAwMDAwMCB9IAoJPC9zdHlsZT4KCTxnIGlkPSJMYXllciI+CgkJPHBhdGggaWQ9IkxheWVyIiBjbGFzcz0ic2hwMCIgZD0iTTUxLjggMjIuNkwzMC42IDM5LjZDMzAuMiAzOS45IDI5LjggNDAgMjkuNCA0MEwxNyA0MEMxNS45IDQwIDE1IDQwLjkgMTUgNDJMMTUgNThDMTUgNTkuMSAxNS45IDYwIDE3IDYwTDI5LjMgNjBDMjkuOCA2MCAzMC4yIDYwLjIgMzAuNSA2MC40TDUxLjcgNzcuNEM1MyA3OC40IDU0LjkgNzcuNSA1NC45IDc1LjhMNTQuOSAyNC4yQzU1IDIyLjUgNTMuMSAyMS42IDUxLjggMjIuNloiIC8+CgkJPHBhdGggaWQ9IkxheWVyIiBjbGFzcz0ic2hwMCIgZD0iTTY0LjUgMzhDNjMuNyAzNy4yIDYyLjUgMzcuMiA2MS43IDM4QzYwLjkgMzguOCA2MC45IDQwIDYxLjcgNDAuOEM2NC4yIDQzLjMgNjUuNSA0Ni41IDY1LjUgNTBDNjUuNSA1My41IDY0LjEgNTYuNyA2MS43IDU5LjJDNjAuOSA2MCA2MC45IDYxLjIgNjEuNyA2MkM2Mi4xIDYyLjQgNjIuNiA2Mi42IDYzLjEgNjIuNkM2My42IDYyLjYgNjQuMSA2Mi40IDY0LjUgNjJDNjcuNyA1OC44IDY5LjUgNTQuNSA2OS41IDUwQzY5LjUgNDUuNSA2Ny43IDQxLjIgNjQuNSAzOFoiIC8+CgkJPHBhdGggaWQ9IkxheWVyIiBjbGFzcz0ic2hwMCIgZD0iTTY5LjggMzIuN0M2OSAzMS45IDY3LjggMzEuOSA2NyAzMi43QzY2LjIgMzMuNSA2Ni4yIDM0LjcgNjcgMzUuNUM3MC45IDM5LjQgNzMgNDQuNSA3MyA1MEM3MyA1NS41IDcwLjkgNjAuNiA2NyA2NC41QzY2LjIgNjUuMyA2Ni4yIDY2LjUgNjcgNjcuM0M2Ny40IDY3LjcgNjcuOSA2Ny45IDY4LjQgNjcuOUM2OC45IDY3LjkgNjkuNCA2Ny43IDY5LjggNjcuM0M3NC41IDYyLjcgNzcgNTYuNSA3NyA1MEM3NyA0My41IDc0LjUgMzcuMyA2OS44IDMyLjdaIiAvPgoJCTxwYXRoIGlkPSJMYXllciIgY2xhc3M9InNocDAiIGQ9Ik03NSAyNy40Qzc0LjIgMjYuNiA3MyAyNi42IDcyLjIgMjcuNEM3MS40IDI4LjIgNzEuNCAyOS40IDcyLjIgMzAuMkM3Ny41IDM1LjUgODAuNCA0Mi41IDgwLjQgNTBDODAuNCA1Ny41IDc3LjUgNjQuNSA3Mi4yIDY5LjhDNzEuNCA3MC42IDcxLjQgNzEuOCA3Mi4yIDcyLjZDNzIuNiA3MyA3My4xIDczLjIgNzMuNiA3My4yQzc0LjEgNzMuMiA3NC42IDczIDc1IDcyLjZDODEgNjYuNiA4NC40IDU4LjUgODQuNCA1MEM4NC40IDQxLjUgODEuMSAzMy40IDc1IDI3LjRaIiAvPgoJPC9nPgo8L3N2Zz4="

load_captcha();
