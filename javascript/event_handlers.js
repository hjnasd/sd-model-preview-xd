// Sync the refresh button for list with the invisible refresh button in the extension
function registerClickEvents(refreshButton, invisible_button_id_selectors) {
  // Check if the button element exists and is not null
  if (typeof refreshButton != "undefined" && refreshButton != null) {
    // Only register a new event if you havent already
    if (refreshButton.getAttribute('md_preview_listener') !== 'true') {
      // Set this attribute to true so we dont set the same listener again
      refreshButton.setAttribute('md_preview_listener', 'true');
      // Add a click event listener to the main refresh model button
      refreshButton.addEventListener('click', (event) => {
        // For each button selector in the button selector list, click that button
        invisible_button_id_selectors.forEach(invisible_button_id_selector => {
          // Get the preview refresh model button element
          const previewRefreshModelButton = gradioApp().querySelector(invisible_button_id_selector);
          // Check if the button element exists and is not null
          if (typeof previewRefreshModelButton != "undefined" && previewRefreshModelButton != null) {
            // Click the preview refresh model button after 500ms (gives it a bit to load)
            setTimeout((event) => {
              previewRefreshModelButton.click();
            }, 500);
          }
        });
      });
    }
  }
}

// Sync the value of the selected model from the main SD model list to the model list of this extension
function setSelectValue(selectPreviewModelElement, selectSDModelElement) {
  // Check if the element exists, is not null, and its value is different than the SD model checkpoint
  if(typeof selectPreviewModelElement != "undefined" && selectPreviewModelElement != null &&
    selectPreviewModelElement.value != selectSDModelElement.value) {
    // Set the value of the preview model list to the value of the SD model checkpoint
    selectPreviewModelElement.value = selectSDModelElement.value;
    // Get the options of the preview model list as an array
    const options = Array.from(selectPreviewModelElement.options);
    // Find the option in the array that has the same text as the SD model checkpoint value
    const optionToSelect = options.find(item => item.text == selectSDModelElement.value);
    // Check if the option was found and is not null
    if(typeof optionToSelect != "undefined" && optionToSelect != null) {
      // Mark the option as selected
      optionToSelect.selected = true;
      // Dispatch a change event on the preview model list
      selectPreviewModelElement.dispatchEvent(new Event('change'));
    }
  }
}

// Is fired by automatic1111 when the UI is updated
onUiUpdate(function() {
  // Get the select element for the SD model checkpoint
  const selectSDModelElement = gradioApp().querySelector('#setting_sd_model_checkpoint select');
  // Check if the element exists and is not null
  if(typeof selectSDModelElement != "undefined" && selectSDModelElement != null) {
    // Get the select element for the preview model list
    const selectPreviewModelElement = gradioApp().querySelector('#cp_mp2_preview_model_list select');
    // Only register a new event if you havent already
    if (selectPreviewModelElement != "undefined" && selectPreviewModelElement != null && selectSDModelElement.getAttribute('md_preview_listener') !== 'true') {
      // Set this attribute to true so we dont set the same listener again
      selectSDModelElement.setAttribute('md_preview_listener', 'true');
      // Add an event handler that will update the select with the new value if someone changes the checkpoint
      selectSDModelElement.addEventListener('change', (event) => setSelectValue(selectPreviewModelElement, selectSDModelElement));
      // Check if the element exists, is not null, but its value is not set
      if(typeof selectPreviewModelElement != "undefined" && selectPreviewModelElement != null &&
        (typeof selectPreviewModelElement.value == "undefined" || selectPreviewModelElement.value == null ||
        selectPreviewModelElement.value == "")) {
        // Set the value after 100ms
        setTimeout((event) => {
          setSelectValue(selectPreviewModelElement, selectSDModelElement);
        }, 500);
      }
    }
  }

  /* ################### v DEPRICATED v ############################ */

  // Get the select element for the SD model checkpoint
  const selectHypernetworkElement = gradioApp().querySelector('#setting_sd_hypernetwork select');
  // Check if the element exists and is not null
  if(typeof selectHypernetworkElement != "undefined" && selectHypernetworkElement != null) {
    // Get the select element for the preview model list
    const selectPreviewModelElement = gradioApp().querySelector('#hn_mp2_preview_model_list select');
    // Only register a new event if you havent already
    if (selectPreviewModelElement != "undefined" && selectPreviewModelElement != null && selectHypernetworkElement.getAttribute('md_preview_listener') !== 'true') {
      // Set this attribute to true so we dont set the same listener again
      selectHypernetworkElement.setAttribute('md_preview_listener', 'true');
      // Add an event handler that will update the select with the new value if someone changes the checkpoint
      selectHypernetworkElement.addEventListener('change', (event) => setSelectValue(selectPreviewModelElement, selectHypernetworkElement));
      // Check if the element exists, is not null, but its value is not set
      if(typeof selectPreviewModelElement != "undefined" && selectPreviewModelElement != null &&
        (typeof selectPreviewModelElement.value == "undefined" || selectPreviewModelElement.value == null ||
        selectPreviewModelElement.value == "")) {
        // Set the value after 1000ms
        setTimeout((event) => {
          setSelectValue(selectPreviewModelElement, selectHypernetworkElement);
        }, 500);
      }
    }
  }

  // Sync the refresh hypernetworks list button
  registerClickEvents(gradioApp().querySelector('#refresh_sd_hypernetwork'), ['#hn_modelpreview_xd_refresh_sd_model']);

  // Sync the refresh lora model list buttons
  gradioApp().querySelectorAll('#img2img_script_container button, #txt2img_script_container button').forEach(function(button) {
    if(button.innerHTML === 'Refresh models') {
      registerClickEvents(button, ['#lo_modelpreview_xd_refresh_sd_model']);
    }
  });
  
  /* ################### ^ DEPRICATED ^ ############################ */

  // Sync the refresh main model list button
  registerClickEvents(gradioApp().querySelector('#refresh_sd_model_checkpoint'), ['#cp_modelpreview_xd_refresh_sd_model']);

  // Sync the new refresh extra network buttons to this extension
  registerClickEvents(gradioApp().querySelector('#txt2img_extra_refresh'), ['#cp_modelpreview_xd_refresh_sd_model','#lo_modelpreview_xd_refresh_sd_model','#hn_modelpreview_xd_refresh_sd_model','#em_modelpreview_xd_refresh_sd_model']);
  registerClickEvents(gradioApp().querySelector('#img2img_extra_refresh'), ['#cp_modelpreview_xd_refresh_sd_model','#lo_modelpreview_xd_refresh_sd_model','#hn_modelpreview_xd_refresh_sd_model','#em_modelpreview_xd_refresh_sd_model']);

  // Find the radio buttons used in the setting page and add a tooltip to them
  let name_matching_setting = gradioApp().querySelector("#settings_model_preview_xd #setting_model_preview_xd_name_matching .gr-input-label:not([title])")
  if (typeof name_matching_setting != "undefined" && name_matching_setting != null) {
    // Get the span from the button that contains the text
    let labelText = name_matching_setting.querySelector("span");
    if(typeof labelText != "undefined" && labelText != null && typeof labelText.innerText != "undefined" && labelText.innerText != null) {
      // Depending on the label text, choose an appropriate tooltip
      let title = "";
      switch (labelText.innerText) {
        case "Loose":
          title = "Use a loose naming scheme for matching preview files. Your preview files must contain the model name somewhere in their file name. If your model is named 'model.ckpt' your preview files must be named in the following manner:\n • mymodel.html\n • model_markdown.md\n • trigger_words_for_model.txt\n • model-image.webp\n • model.preview.png\n • my3Dmodel.jpg\n • modelling.jpeg";
        break;
        case "Strict":
          title = "Use a strict naming scheme for matching preview files. If your model is named 'model.ckpt' your preview files must be named in the following manner:\n • model.html\n • model.md\n • model.txt\n • model.webp\n • model.preview.png\n • model.3.jpg\n • model.preview.4.jpeg";
        break;
        case "Folder":
          title = "Use folder name matching. Will look for a folder within your model directory that matches your model's name (case sensitive) and will show any preview files found within that folder or any subfolders of that folder. If your model is named 'mymodel.ckpt' all preview files located in '/mymodel/' will be shown.";
        break;
      }
      if (title != "") {
        // add the tooltip to the label
        name_matching_setting.setAttribute("title", title);
      }
    }
  }
})

function metaDataCopy(event) {
  // get the textarea next to the image icon that has the meta data in it
  const textarea = event.target.nextElementSibling;
  // add the text from the textarea to the clipboard
  navigator.clipboard.writeText(textarea.value);
}

function imageZoomIn(event) {
  // click event for images that creates an overlay div and houses a copy of the image showing fullscreen
  
  // get the image that was clicked on
  const image = event.target;
  // create the overlay div to black out the rest of the website
  const overlay = document.createElement("div");
  // add styling to the overlay div
  overlay.style = "position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.9); z-index: 999;	transition: all 0.2s ease-in-out;	cursor: zoom-out;"
  // create a copy of the image in the overlay div
  overlay.innerHTML = `<img src="${image.src}" style="width: 90%;	height: 90%; position: absolute;	top: 50%;	left: 50%; transform: translate(-50%, -50%);	object-fit: contain;">`;
  // add an click event to the overlay that will delete the overlay when its clicked
  overlay.addEventListener("click", function() {
		overlay.remove();
	});
  // append the overlay div to the body
  document.body.appendChild(overlay);
}