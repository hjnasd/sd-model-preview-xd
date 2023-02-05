# sd-model-preview-xd
Extension for [Automatic1111 Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) to display previews for custom models[^1].

[^1]: This extension should support all operating systems in theory but has only been tested in Windows

## About
With so many new models appearing it's becoming harder to keep track of what models output what styles and what tags are used to call these styles.
This extension allows you to create various types of preview files/notes, each with the same name as your model and have this info easily displayed for later reference in webui.

## Installation
1. From the extensions tab in web ui click install from url
2. Paste `https://github.com/CurtisDS/sd-model-preview-xd` into the url box.
3. Click Install
4. From the Installed tab click apply and restart[^2].
5. Put `.html`[^3], `.md`[^3], `.txt`, `.png`, `.webp`, and/or `.jpg`/`.jpeg` files in the same directory as your models, or a subfolder. Make sure to name the files the same as your model. You may append something after the name of the model and it will still work ([See: Name Matching Rules](#name-matching-rules)). You can have multiple images for a single model, but only one markdown, text, or html file. You can also mix and match any of the preview files except for HTML files, if the extension finds an html file it will only show the html file.

[^2]: If you run into issues after first install you may need to fully shutdown and rerun the webui-user.bat after you install the extension.
[^3]: HTML and Markdown files will not support linking to files or images outside of the Automatic1111 directory. If you cannot keep linked files within the install directory upload them to the internet and link to them remotely.

***Note**: If you are using symlinks or otherwise changing the default model directories [click here for information](#changing-default-directories)*

For example if you have `my_model.ckpt` in `models\Stable-diffusion` then you can put `my_model.txt`, `my_model_1.jpg` and, `my_model_2.jpg` in `models\Stable-diffusion\Previews` and it will display them in the "Model Preview" tab.

This extension supports the folling model types in the the default directories:

- SD Checkpoints
- Embeddings
- Hypernetworks
- LoRA

## Usage
1. After creating the preview files and putting them in the corresponding directories, select the Model Preview tab in web ui and then the type of model you want to preview
2. Select a model from the dropdown list. (If the model has any preview files they will be shown)
3. Any preview png files found that also contain prompt data embedded in them will have a red "copy" button when hovering over the image. By clicking the button it will copy the prompt data to your clipboard.

![screenshot](https://github.com/CurtisDS/sd-model-preview-xd/raw/main/sd-model-preview-xd.png)

## Tips

1. You can save the `README.md` file from a models huggingface page to use as your model preview:

      ![screenshot of markdown example](https://github.com/CurtisDS/sd-model-preview-xd/raw/main/sd-model-preview-xd-markdown-example.png)

2. You can save the model's Civitai page (using <kbd>Ctrl</kbd>+<kbd>S</kbd> in your browser) to use the Civitai page as your model preview:
      
      ![screenshot of html example](https://github.com/CurtisDS/sd-model-preview-xd/raw/main/sd-model-preview-xd-html-example.png)

3. If you want to keep it clean, create a simple .txt file with the trigger words and save a few sample images:

      ![screenshot of text and images example](https://github.com/CurtisDS/sd-model-preview-xd/raw/main/sd-model-preview-xd-text-and-image-example.png)

4. You can now taken linked directly to the preview files of a model by clicking on the `ⓘ` in the extra networks thumbnail cards.

      - When `Default view for Extra Networks` is set to `cards`:

          ![image](https://user-images.githubusercontent.com/20732674/216813267-c8539ae3-c318-42fa-b5db-f89176993fbc.png)

      - When `Default view for Extra Networks` is set to `thumbs`:

          ![image](https://user-images.githubusercontent.com/20732674/216813283-2e4f874f-3afa-4088-98eb-95bff0566ec8.png)

## Things to watch out for

### Name Matching Rules

In the settings tab there is a page for Model Preivew XD where you can update the setting to use "Strict", "Loose", or "Folder" naming. Depending on that setting the rules for naming preview files will be slightly different.

- #### Strict Name Matching:

  Name your preview files the exact same as the model name. To support multiple images you can also choose to append to the model name `.preview` and/or `.1` (where 1 can be any number). 

  Here are a number of examples that will work with strict naming assuming your model is named `model.ckpt`:

  - model.txt
  - model.md
  - model.html
  - model.png
  - model.preview.png
  - model.4.png
  - model.preview.7.png

  ***Note** that in the example png images were used but you can use png, jpg, jpeg, or webm images*

- #### Loose Name Matching:

  The naming rule loose name matching preview files is that your model name has to appear anywhere in the file name. Please note this has the potential to return preview files for other models that are named similarly. For example, if you have a model named `my-checkpoint.ckpt` and `my-checkpoint2.ckpt` the extension will pick up preview files meant for `my-checkpoint2` in its search for preview files for `my-checkpoint`. You can avoid this my renaming `my-checkpoint` to `my-checkpoint1` (*Make sure to also update any existing preview files*).

  Here are a number of examples that will work with loose naming assuming your model is named `model.ckpt`:

  - model_trigger_words.txt
  - model_readme.md
  - my_model_webpage.html
  - model.png
  - model_preview.png
  - model.image.png
  - 3D_modelling_checkpoint.png

  ***Note** that in the example png images were used but you can use png, jpg, jpeg, or webm images*

  ***Also note** that preview files that appear to be for other checkpoints have also been returned*

- #### <u>Folder Name Matching:</u>

  When using folder name matching the extension will look for a folder matching your model name and return any preview files found within, including subdirectories.

  Here are a number of examples that will work with folder naming assuming your model is named `model.ckpt`:

  - /Stable-diffusion/model/trigger_words.txt
  - /Stable-diffusion/model/readme.md
  - /Stable-diffusion/model/info.html
  - /Stable-diffusion/model/0.png
  - /Stable-diffusion/model/preview.png

  ***Note** that in the example png images were used but you can use png, jpg, jpeg, or webm images*

### Changing Default Directories

Gradio (the software Automatic1111 is built on) doesn't support linking to files outside of the Automatic1111 install directory through the webui. So if you have used symlinks or Automatic1111's built in command line arguments to change the directories for your models to something outside of the Automatic1111 directory you will need to take advantage of one of the following workarounds for your previews to work.

1. If you use the command line arguments to change the directories for your models the extension will look in both the default directories and the custom directories for preview files. So you could change the directory for your models and leave your preview files in the default directories, this will keep them within the install directory and remove the issues with linking.

      <details>
      <summary>Click here for a quick guide on how to change directories without using symlinks.</summary>
      ​

      If you want to change the directories for models add these settings to your `webui-user.bat` `COMMANDLINE_ARGS` for each model type:

      `--ckpt-dir "D:\\my models\\checkpoints"`

      `--hypernetwork-dir "D:\\my models\\hypernetworks"`

      `--embeddings-dir "D:\\my models\\embeddings"`

      `--lora-dir "D:\\my models\\lora"`

      If you wanted to use all the settings at once your COMMANDLINE_ARGS line would look something like this:

      ```bash
      set COMMANDLINE_ARGS=--xformers --api --ckpt-dir "D:\\my models\\checkpoints" --hypernetwork-dir "D:\\my models\\hypernetworks" --embeddings-dir "D:\\my models\\embeddings" --lora-dir "D:\\my models\\lora"
      ```

      </details>

2. The extension can detect if a preview file is outside of the install directory and alter how it handles the preview to try and avoid some of the issues with linking files in the webui. The following differences will occur:
- **Text files**: Nothing will change, it will work the same as if it was in the install directory.

- **Image files**: The images will be converted to a base64 string essensially copying the image into the html code instead of linking to a file. This may slightly increase load times but should be otherwise fine.

- **Markdown files**: The preview will load but if you linked to a local image or file in the markdown - even if that file or image is in the same directory as the markdown file - it may not resolve that link. A workaround would be to upload files or images to the internet and link to them remotely instead of locally, then the links will resolve.

- **HTML files**: Normally the extension will create an `<iframe>` linking to the HTML file, however again because you cannot link to files it will now convert the file to a base64 string and use that in the `<iframe>` instead. Also, as with markdown files if you linked to a local image or file in the HTML code it may not resolve that link. You can use the same workaround, though, which is to upload the files or images to the internet and link to them remotely instead of locally.
