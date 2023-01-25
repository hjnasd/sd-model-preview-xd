# sd-model-preview-xd
Extension for [Automatic1111 Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) to display previews for custom models.

## About
With so many new models appearing it's becoming harder to keep track of what models output what styles and what tags are used to call these styles.
This extension allows you to create various types of preview files/notes, each with the same name as your model and have this info easily displayed for later reference in webui.

## Installation
1. From the extensions tab in web ui click install from url
2. Paste `https://github.com/CurtisDS/sd-model-preview-xd` into the url box.
3. Click Install
4. From the Installed tab click apply and restart  (*If you run into issues you may need to fully shutdown and rerun the webui-user.bat*).
5. Put `.html`, `.md`, `.txt`, `.png`, `.webp`, and/or `.jpg`/`.jpeg` files in the same directory as your models, or a subfolder. Make sure to name the files the same as your model. You may append something after the name of the model and it will still work. You can have multiple images for a single model, but only one markdown, text, or html file. You can also mix and match any of the preview files except for HTML files, if the extension finds an html file it will only show the html file.

***Note**: Symlinks do not seem to be supported see further down for a workaround*

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

4. Watch out for name collisions! If you have a model named `my-checkpoint.ckpt` and `my-checkpoint2.ckpt` the extension will pick up preview files meant for `my-checkpoint2` in its search for preview files for `my-checkpoint`. You can avoid this my renaming `my-checkpoint` to `my-checkpoint1` (*Make sure to also update any existing preview files*).

## Symlink workaround

The latest version of gradio (the software Automatic1111 is built on) doesn't seem to support symlinks for linking files in the webui. To work around this use Automatic1111's built in arguments for altering the model directories.

Edit your `web-user.bat` `COMMANDLINE_ARGS` to include the custom directory argument for each model type:

`--ckpt-dir "D:\\my models\\checkpoints"`

`--hypernetwork-dir "D:\\my models\\hypernetworks"`

`--embeddings-dir "D:\\my models\\embeddings"`

`--lora-dir "D:\\my models\\lora"`

If you wanted to use all the settings at once your COMMANDLINE_ARGS line would look something like this:

```
set COMMANDLINE_ARGS=--xformers --api --ckpt-dir "D:\\my models\\checkpoints" --hypernetwork-dir "D:\\my models\\hypernetworks" --embeddings-dir "D:\\my models\\embeddings" --lora-dir "D:\\my models\\lora"
```

**Note about using arguments to change the model directories:**

If you change one of the model directories to point to a directory outside of your Automatic1111 install directory please note that it is suggested you keep your preview files in the default directories (they will still be loaded).

If you must put your preview files in a directory outside of the Automatic1111 directory keep in mind that images will be referenced by converting them to base64 strings which could cause more load times (probably minor) and if you use an html or markdown preview file that internally links to another file on the local system there may be issues with resolving those links due to the limitations of the webui server.

Again, for best support it is recommended that you keep your preview files within the default directories but at least basic support is there if you choose not to.

---
<sub>This extension should support all operating systems in theory but has only been tested in Windows</sub>
