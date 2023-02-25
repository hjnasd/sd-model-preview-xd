import os
import os.path
import re
import gradio as gr
from modules import script_callbacks, sd_models, shared, sd_hijack
from PIL import Image
import base64

import importlib.util

def import_lora_module():
	# import/update the lora module if its available
	try:
		spec = importlib.util.find_spec('extensions.sd-webui-additional-networks.scripts.model_util')
		if spec:
			additional_networks = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(additional_networks)
		else:
			additional_networks = None
	except:
		additional_networks = None
	return additional_networks

def import_lora_module_builtin():
	# import/update the lora module if its available from the builtin extensions
	try:
		spec = importlib.util.find_spec('extensions-builtin.Lora.lora')
		if spec:
			additional_networks_builtin = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(additional_networks_builtin)
		else:
			additional_networks_builtin = None
	except:
		additional_networks_builtin = None
	return additional_networks_builtin

# try and get the lora module
additional_networks = import_lora_module()
additional_networks_builtin = import_lora_module_builtin()

refresh_symbol = '🔄'
update_symbol = '↙️'

def is_subdirectory(parent_dir, child_dir):
	# checks if the child directory is actually a child directory of the parent directory
	parent_dir = os.path.abspath(os.path.realpath(parent_dir))
	child_dir = os.path.abspath(os.path.realpath(child_dir))

	if not os.path.isdir(parent_dir) or not os.path.isdir(child_dir):
		return False

	common_prefix = os.path.commonprefix([parent_dir, child_dir])
	return common_prefix == parent_dir and child_dir != parent_dir

def is_dir_in_list(dir_list, check_dir):
	# Convert all directories in the list to absolute paths
	dir_list = [os.path.abspath(d) for d in dir_list]
	# Convert the specified directory to an absolute path
	check_dir = os.path.abspath(check_dir)
	# Check if the specified directory is in the list of directories
	for dir_path in dir_list:
		if os.path.samefile(check_dir, dir_path):
			return True
	return False

# keep a copy of the choices to give control to user when to refresh
checkpoint_choices = []
embedding_choices = []
hypernetwork_choices = []
lora_choices = []

def list_all_models():
	global checkpoint_choices
	# gets the list of checkpoints
	model_list = sd_models.checkpoint_tiles()
	checkpoint_choices = sorted(model_list, key=lambda x: x.lower())
	return checkpoint_choices

def list_all_embeddings():
	global embedding_choices
	# get the list of embeddings
	list = [x for x in sd_hijack.model_hijack.embedding_db.word_embeddings.keys()]
	list.extend([x for x in sd_hijack.model_hijack.embedding_db.skipped_embeddings.keys()])
	embedding_choices = sorted(list, key=lambda x: x.lower())
	return embedding_choices

def list_all_hypernetworks():
	global hypernetwork_choices
	# get the list of hyperlinks
	list = [x for x in shared.hypernetworks.keys()]
	hypernetwork_choices = sorted(list, key=lambda x: x.lower())
	return hypernetwork_choices
	
def list_all_loras():
	global lora_choices, additional_networks, additional_networks_builtin
	# create an empty set for lora models
	loras = set()

	# import/update the lora module
	additional_networks = import_lora_module()
	if additional_networks is not None:
		# copy the list of models
		loras_list = additional_networks.lora_models.copy()
		# remove the None item from the lsit
		loras_list.pop("None", None)
		# remove hash from model
		loras_list = [re.sub(r'\([a-fA-F0-9]{10,12}\)$', '', model) for model in loras_list.keys()]
		loras.update(loras_list)

	# import/update the builtin lora module
	additional_networks_builtin = import_lora_module_builtin()
	if additional_networks_builtin is not None:
		# copy the list of models
		loras_list = additional_networks_builtin.available_loras.copy()
		# remove the None item from the lsit
		loras_list.pop("None", None)
		loras.update(loras_list.keys())

	# return the list
	lora_choices = sorted(loras, key=lambda x: x.lower())
	return lora_choices

def refresh_models():
	global checkpoint_choices
	# update the choices for the checkpoint list
	checkpoint_choices = list_all_models()
	return gr.Dropdown.update(choices=checkpoint_choices)

def refresh_embeddings():
	global embedding_choices
	# update the choices for the embeddings list
	embedding_choices = list_all_embeddings()
	return gr.Dropdown.update(choices=embedding_choices)

def refresh_hypernetworks():
	global hypernetwork_choices
	# update the choices for the hypernetworks list
	hypernetwork_choices = list_all_hypernetworks()
	return gr.Dropdown.update(choices=hypernetwork_choices)

def refresh_loras():
	global lora_choices
	# update the choices for the lora list
	lora_choices = list_all_loras()
	return gr.Dropdown.update(choices=lora_choices)

def update_checkpoint(name):
	# update the selected preview for checkpoint tab
	new_choice = find_choice(checkpoint_choices, name)
	return new_choice, *show_model_preview(new_choice)

def update_embedding(name):
	# update the selected preview for embedding tab
	new_choice = find_choice(embedding_choices, name)
	return new_choice, *show_embedding_preview(new_choice)

def update_hypernetwork(name):
	# update the selected preview for hypernetwork tab
	new_choice = find_choice(hypernetwork_choices, name)
	return new_choice, *show_hypernetwork_preview(new_choice)

def update_lora(name):
	# update the selected preview for lora tab
	new_choice = find_choice(lora_choices, name)
	return new_choice, *show_lora_preview(new_choice)

def find_choice(list, name):
	# clean the name from the list and match a choice to the model 
	# TODO there could be name collisions here that may need to be handled in the future.
	for choice in list:
		cleaned_name = clean_modelname(choice)
		if cleaned_name == name:
			return choice
	return name

def create_html_iframe(file, is_in_a1111_dir):
	if is_in_a1111_dir:
		# create the iframe html code
		html_code = f'<iframe src="file={file}"></iframe>'
	else:
		html_code = ""
		# the html file isnt located in the a1111 directory so load the html file as a base64 string instead of linking to it
		with open(file, 'rb') as html_file:
			html_data = base64.b64encode(html_file.read()).decode()
			html_code = f'<iframe src="data:text/html;charset=UTF-8;base64,{html_data}"></iframe>'
	return html_code

def create_html_img(file, is_in_a1111_dir):
	# create the html to display an image along with its meta data
	image = Image.open(file)
	# load the image to memory (needed for getting the meta data)
	image.load()
	# get the prompt data
	metadata = image.info.get("parameters", None)

	# set default order to 0
	order = 0
	# if strict naming is on, search the file name for a number at the end of the file and use that for its order
	if shared.opts.model_preview_xd_name_matching == "Strict":
		# get the file name without extension
		file_name, file_extension = os.path.splitext(os.path.basename(file))
		# search for '{anything}.{number}' in the file name and return the number
		image_number = re.search(".*\.(\d+)$", file_name)
		order = int(image_number.group(1)) if image_number else 0

	if is_in_a1111_dir:
		# replace the file name string spaces with %20 so the path will work
		space_replace = file.replace(" ","%20")
		# create the html for the image
		html_code = f'<div class="img-container" style="order:{order}"><img src=file={space_replace} onclick="imageZoomIn(event)" />'
	else:
		# linking to the image wont work so convert it to a base64 byte string
		with open(file, "rb") as img_file:
			img_data = base64.b64encode(img_file.read()).decode()
		# create the html for the image
		html_code = f'<div class="img-container" style="order:{order}"><img src="data:image/{image.format};base64,{img_data}" onclick="imageZoomIn(event)" />'

	# if the image has prompt data in the meta data also add some elements to support copying the prompt to clipboard
	if metadata is not None and metadata.strip() != "":
		html_code += '<div class="img-meta-ico" title="Copy Metadata" onclick="metaDataCopy(event)"></div>'
		html_code += f'<textarea class="img-meta">{metadata}</textarea>'
	html_code += "</div>\n"
	# return the html code
	return html_code

def natural_order_number(s):
	# split a string into segments of strings and ints that will be used to sort naturally
    return [int(x) if x.isdigit() else x for x in re.split('(\d+)', s)]

def search_and_display_previews(model_name, paths):
	# create patters for the supported preview file types
	# `model_name` will be the name of the model to check for preview files for
	if shared.opts.model_preview_xd_name_matching == "Strict":
		# strict naming is intended to avoid name collision between 'checkpoint1000' and 'checkpoint10000'.
		# Using a loose naming rule preview files for 'checkpoint10000' would show up for 'checkpoint1000'
		# The rules for strict naming are:
		# HTML previews should follow {model}.html example 'checkpoint1000.html'
		html_pattern = re.compile(r'^' + re.escape(model_name) + r'(?i:\.html)$')
		# Markdown previews should follow {model}.md example 'checkpoint1000.md'
		md_pattern = re.compile(r'^' + re.escape(model_name) + r'(?i:\.md)$')
		# Text files previews should follow {model}.txt example 'checkpoint1000.txt'
		txt_pattern = re.compile(r'^' + re.escape(model_name) + r'(?i:\.txt)$')
		# Images previews should follow {model}.{extension} or {model}.preview.{extension} or {model}.{number}.{extension} or {model}.preview.{number}.{extension}
		# example 1 'checkpoint1000.png'
		# example 2 'checkpoint1000.preview.jpg'
		# example 3 'checkpoint1000.1.jpeg'
		# example 4 'checkpoint1000.preview.1.webp'
		img_pattern = re.compile(r'^' + re.escape(model_name) + r'(?i:(\.preview)?(\.\d+)?\.(png|jpg|jpeg|webp|jxk|avif))$')
	elif shared.opts.model_preview_xd_name_matching == "Folder":
		# use a folder name matching that only requires the model name to show up somewhere in the folder path not the file name name
		html_pattern = re.compile(r'^.*(?i:\.html)$')
		md_pattern = re.compile(r'^.*(?i:\.md)$')
		txt_pattern = re.compile(r'^.*(?i:\.txt)$')
		img_pattern = re.compile(r'^.*(?i:\.(png|jpg|jpeg|webp|jxk|avif))$')
	else:
		# use a loose name matching that only requires the model name to show up somewhere in the file name
		html_pattern = re.compile(r'^.*' + re.escape(model_name) + r'.*(?i:\.html)$')
		md_pattern = re.compile(r'^.*' + re.escape(model_name) + r'.*(?i:\.md)$')
		txt_pattern = re.compile(r'^.*' + re.escape(model_name) + r'.*(?i:\.txt)$')
		img_pattern = re.compile(r'^.*' + re.escape(model_name) + r'.*(?i:\.(png|jpg|jpeg|webp|jxk|avif))$')
	
	# an array to hold the image html code
	html_code_list = []
	# if a text file is found
	found_txt_file = None
	# if a markdown file is found
	md_file = None

	# get the current directory so we can convert absolute paths to relative paths if we need to
	current_directory = os.getcwd()

	# support the ability to check multiple paths
	for path in paths:
		# check if the path is a subdirectory of the install directory
		is_in_a1111_dir = is_subdirectory(current_directory, path)

		# loop through all files in the path and any subdirectories
		for dirpath, dirnames, filenames in os.walk(path, followlinks=True):
			# get a list of all parent directories
			directories = dirpath.split(os.path.sep)
			# if we are not using folder match mode look for files normally otherwise we are using folder match mode so make sure at least one parent directory is equal to the name of the model
			if shared.opts.model_preview_xd_name_matching != "Folder" or (shared.opts.model_preview_xd_name_matching == "Folder" and model_name in directories):
				# sort the file names using a natural sort algorithm
				sorted_filenames = sorted(filenames, key=natural_order_number)
				# check each file to see if it is a preview file
				for filename in sorted_filenames:
					file_path = os.path.join(dirpath, filename)
					if html_pattern.match(filename):
						# prioritize html files, if you find one, just return it
						return create_html_iframe(file_path, is_in_a1111_dir), None, None
					if md_pattern.match(filename):
						# there can only be one markdown file, if one was already found it is replaced
						md_file = file_path
					if img_pattern.match(filename):
						# there can be many images, even spread accross the multiple paths
						html_code_list.append(create_html_img(file_path, is_in_a1111_dir))
					if txt_pattern.match(filename):
						# there can only be one text file, if one was already found it is replaced
						found_txt_file = file_path
			
	# if there were images found, wrap the images in a container div
	html_code_output = '<div class="img-container-set">' + ''.join(html_code_list) + '</div>' if len(html_code_list) > 0 else None

	# return the images, and/or text file found
	return html_code_output, md_file, found_txt_file

def clean_modelname(modelname):
	# convert the extension to lowercase if it exists
	name, ext = os.path.splitext(modelname)
	ext = ext.lower()
	modelname = name + ext	
	# remove the extension and the hash if it exists at the end of the model name (this is added by a1111) and 
	# if the model name contains a path (which happens when a checkpoint is in a subdirectory) just return the model name portion
	return re.sub(r"(\.pt|\.bin|\.ckpt|\.safetensors)?( \[[a-fA-F0-9]{10,12}\])?$", "", modelname).split("\\")[-1].split("/")[-1]

def show_model_preview(modelname=None):
	# remove the hash if exists, the extension, and if the string is a path just return the file name
	modelname = clean_modelname(modelname)
	# create list of directories
	directories = [os.path.join('models','Stable-diffusion')] # models/Stable-diffusion
	set_dir = shared.cmd_opts.ckpt_dir
	if set_dir is not None and not is_dir_in_list(directories, set_dir):
		# WARNING: html files and markdown files that link to local files outside of the automatic1111 directory will not work correctly
		directories.append(set_dir)
	# get preview for the model
	return show_preview(modelname, directories)

def show_embedding_preview(modelname=None):
	# remove the hash if exists, the extension, and if the string is a path just return the file name
	modelname = clean_modelname(modelname)
	# create list of directories
	directories = ['embeddings']
	set_dir = shared.cmd_opts.embeddings_dir
	if set_dir is not None and not is_dir_in_list(directories, set_dir):
		# WARNING: html files and markdown files that link to local files outside of the automatic1111 directory will not work correctly
		directories.append(set_dir)
	# get preview for the model
	return show_preview(modelname, directories)

def show_hypernetwork_preview(modelname=None):
	# remove the hash if exists, the extension, and if the string is a path just return the file name
	modelname = clean_modelname(modelname)
	# create list of directories
	directories = [os.path.join('models','hypernetworks')] # models/hypernetworks
	set_dir = shared.cmd_opts.hypernetwork_dir
	if set_dir is not None and not is_dir_in_list(directories, set_dir):
		# WARNING: html files and markdown files that link to local files outside of the automatic1111 directory will not work correctly
		directories.append(set_dir)
	# in older versions of a1111 the hash was included at the end in brackets, remove the hash if you find it
	modelname = re.sub(r"(\([a-fA-F0-9]{10,12}\))?$", "", modelname)
	# get preview for the model
	return show_preview(modelname, directories)

def show_lora_preview(modelname=None):
	# remove the hash if exists, the extension, and if the string is a path just return the file name
	modelname = clean_modelname(modelname)

	# create list of directories
	directories = []

	# add models/lora just in case to the list of directories
	default_dir = os.path.join("models","Lora") # models/Lora
	if os.path.exists(default_dir) and os.path.isdir(default_dir):
		directories.append(default_dir)

	# add directories from the builtin lora extension if exists
	set_dir = shared.cmd_opts.lora_dir
	if set_dir is not None and not is_dir_in_list(directories, set_dir):
		# WARNING: html files and markdown files that link to local files outside of the automatic1111 directory will not work correctly
		directories.append(set_dir)

	# add directories from the thirdparty lora extension if exists
	if additional_networks is not None:
		# use the same pattern as the additional_networds.py extention to build up a list of paths to check for lora models and preview files
		set_dir = additional_networks.lora_models_dir
		if set_dir is not None and not is_dir_in_list(directories, set_dir):
			directories.append(set_dir)
		extra_lora_path = shared.opts.data.get("additional_networks_extra_lora_path", None)
		if extra_lora_path and os.path.exists(extra_lora_path) and not is_dir_in_list(directories, extra_lora_path):
			directories.append(extra_lora_path)

	# in older versions of a1111 the hash was included at the end in brackets, remove the hash if you find it
	modelname = re.sub(r"(\([a-fA-F0-9]{10,12}\))?$", "", modelname)
	# get preview for the model
	return show_preview(modelname, directories)

def show_preview(name, paths):
	# get the preview data
	html_code, found_md_file, found_txt_file = search_and_display_previews(name, paths)
	preview_html = '' if html_code is None else html_code

	# if a text file was found update the gradio text element
	if found_txt_file:
		output_text = ""
		with open(found_txt_file, "r", encoding="utf8") as file:
			for line in file:
				output_text = f'{output_text}{line.strip()}\n'
		txt_update = gr.Textbox.update(value=output_text, visible=True)
	else:
		txt_update = gr.Textbox.update(value=None, visible=False)
	
	# if a markdown file was found update the gradio markdown element
	if found_md_file:
		output_text = ""
		with open(found_md_file, "r", encoding="utf8") as file:
			output_text = file.read()
		md_update = gr.Textbox.update(value=output_text, visible=True)
	else:
		md_update = gr.Textbox.update(value=None, visible=False)
	
	# if images were found or an HTML file was found update the gradio html element
	if html_code:
		html_update = gr.HTML.update(value=preview_html, visible=True)
	else:
		html_update = gr.HTML.update(value='', visible=False)

	# if nothing was found display a message that nothing was found
	if found_txt_file is None and found_md_file is None and (html_code is None or len(html_code) == 0):
		html_update = gr.HTML.update(value="<span style='margin-left: 1em;'>No Preview Found</span>", visible=True)
	return txt_update, md_update, html_update

def on_ui_tabs():
	global additional_networks, additional_networks_builtin
	# import/update the lora module
	additional_networks = import_lora_module()
	additional_networks_builtin = import_lora_module_builtin()

	# create a gradio block
	with gr.Blocks() as modelpreview_interface:

		# create a tab for the checkpoint previews
		with gr.Tab("Checkpoints", elem_id="model_preview_xd_checkpoints_tab"):
			with gr.Row():
				checkpoints_list = gr.Dropdown(label="Model", choices=list_all_models(), interactive=True, elem_id="cp_mp2_preview_model_list")
			with gr.Row(elem_id="cp_modelpreview_xd_hidden_ui"):
				refresh_checkpoint = gr.Button(value=refresh_symbol, elem_id="cp_modelpreview_xd_refresh_sd_model")
				update_checkpoint_name = gr.Textbox(value="", elem_id="cp_modelpreview_xd_update_sd_model_text")
				update_checkpoint_button = gr.Button(value=update_symbol, elem_id="cp_modelpreview_xd_update_sd_model")
			with gr.Row():
				checkpoint_text_area = gr.Textbox(label='Notes', interactive=False, lines=1, visible=False)
			with gr.Row(elem_id="cp_modelpreview_xd_html_row"):
				with gr.Row(elem_id="cp_modelpreview_xd_flexcolumn_row"):
					checkpoint_preview_html = gr.HTML(elem_id="cp_modelpreview_xd_html_div", visible=False)
					checkpoint_preview_md = gr.Markdown(elem_id="cp_modelpreview_xd_markdown_div", visible=False)

		checkpoints_list.change(
			fn=show_model_preview,
			inputs=[
				checkpoints_list,
			],
			outputs=[
				checkpoint_text_area,
				checkpoint_preview_md,
				checkpoint_preview_html,
			]
		)

		refresh_checkpoint.click(
			fn=refresh_models,
			inputs=[],
			outputs=[
				checkpoints_list,
			]
		)

		update_checkpoint_button.click(
			fn=update_checkpoint,
			inputs=[
				update_checkpoint_name,
			],
			outputs=[
				checkpoints_list,
				checkpoint_text_area,
				checkpoint_preview_md,
				checkpoint_preview_html,
			]
		)

		# create a tab for the embedding previews
		with gr.Tab("Embeddings", elem_id="model_preview_xd_embeddings_tab"):
			with gr.Row():
				embeddings_list = gr.Dropdown(label="Model", choices=list_all_embeddings(), interactive=True, elem_id="em_mp2_preview_model_list")
			with gr.Row(elem_id="em_modelpreview_xd_hidden_ui"):
				refresh_embedding = gr.Button(value=refresh_symbol, elem_id="em_modelpreview_xd_refresh_sd_model")
				update_embedding_name = gr.Textbox(value="", elem_id="em_modelpreview_xd_update_sd_model_text")
				update_embedding_button = gr.Button(value=update_symbol, elem_id="em_modelpreview_xd_update_sd_model")
			with gr.Row():
				embedding_text_area = gr.Textbox(label='Notes', interactive=False, lines=1, visible=False)
			with gr.Row(elem_id="em_modelpreview_xd_html_row"):
				with gr.Row(elem_id="em_modelpreview_xd_flexcolumn_row"):
					embedding_preview_html = gr.HTML(elem_id="em_modelpreview_xd_html_div", visible=False)
					embedding_preview_md = gr.Markdown(elem_id="em_modelpreview_xd_markdown_div", visible=False)

		embeddings_list.change(
			fn=show_embedding_preview,
			inputs=[
				embeddings_list,
			],
			outputs=[
				embedding_text_area,
				embedding_preview_md,
				embedding_preview_html,
			]
		)

		refresh_embedding.click(
			fn=refresh_embeddings,
			inputs=[],
			outputs=[
				embeddings_list,
			]
		)

		update_embedding_button.click(
			fn=update_embedding,
			inputs=[
				update_embedding_name,
			],
			outputs=[
				embeddings_list,
				embedding_text_area,
				embedding_preview_md,
				embedding_preview_html,
			]
		)

		# create a tab for the hypernetwork previews
		with gr.Tab("Hypernetwork", elem_id="model_preview_xd_hypernetwork_tab"):
			with gr.Row():
				hypernetworks_list = gr.Dropdown(label="Model", choices=list_all_hypernetworks(), interactive=True, elem_id="hn_mp2_preview_model_list")
			with gr.Row(elem_id="hn_modelpreview_xd_hidden_ui"):
				refresh_hypernetwork = gr.Button(value=refresh_symbol, elem_id="hn_modelpreview_xd_refresh_sd_model")
				update_hypernetwork_name = gr.Textbox(value="", elem_id="hn_modelpreview_xd_update_sd_model_text")
				update_hypernetwork_button = gr.Button(value=update_symbol, elem_id="hn_modelpreview_xd_update_sd_model")
			with gr.Row():
				hypernetwork_text_area = gr.Textbox(label='Notes', interactive=False, lines=1, visible=False)
			with gr.Row(elem_id="hn_modelpreview_xd_html_row"):
				with gr.Row(elem_id="hn_modelpreview_xd_flexcolumn_row"):
					hypernetwork_preview_html = gr.HTML(elem_id="hn_modelpreview_xd_html_div", visible=False)
					hypernetwork_preview_md = gr.Markdown(elem_id="hn_modelpreview_xd_markdown_div", visible=False)

		hypernetworks_list.change(
			fn=show_hypernetwork_preview,
			inputs=[
				hypernetworks_list,
			],
			outputs=[
				hypernetwork_text_area,
				hypernetwork_preview_md,
				hypernetwork_preview_html,
			]
		)

		refresh_hypernetwork.click(
			fn=refresh_hypernetworks,
			inputs=[],
			outputs=[
				hypernetworks_list,
			]
		)

		update_hypernetwork_button.click(
			fn=update_hypernetwork,
			inputs=[
				update_hypernetwork_name,
			],
			outputs=[
				hypernetworks_list,
				hypernetwork_text_area,
				hypernetwork_preview_md,
				hypernetwork_preview_html,
			]
		)

		# create a tab for the lora previews if the module was loaded
		if additional_networks is not None or additional_networks_builtin is not None:
			with gr.Tab("Lora", elem_id="model_preview_xd_lora_tab"):
				with gr.Row():
					loras_list = gr.Dropdown(label="Model", choices=list_all_loras(), interactive=True, elem_id="lo_mp2_preview_model_list")
				with gr.Row(elem_id="lo_modelpreview_xd_hidden_ui"):
					refresh_lora = gr.Button(value=refresh_symbol, elem_id="lo_modelpreview_xd_refresh_sd_model")
					update_lora_name = gr.Textbox(value="", elem_id="lo_modelpreview_xd_update_sd_model_text")
					update_lora_button = gr.Button(value=update_symbol, elem_id="lo_modelpreview_xd_update_sd_model")
				with gr.Row():
					lora_text_area = gr.Textbox(label='Notes', interactive=False, lines=1, visible=False)
				with gr.Row(elem_id="lo_modelpreview_xd_html_row"):
					with gr.Row(elem_id="lo_modelpreview_xd_flexcolumn_row"):
						lora_preview_html = gr.HTML(elem_id="lo_modelpreview_xd_html_div", visible=False)
						lora_preview_md = gr.Markdown(elem_id="lo_modelpreview_xd_markdown_div", visible=False)

			loras_list.change(
				fn=show_lora_preview,
				inputs=[
					loras_list,
				],
				outputs=[
					lora_text_area,
					lora_preview_md,
					lora_preview_html,
				]
			)

			refresh_lora.click(
				fn=refresh_loras,
				inputs=[],
				outputs=[
					loras_list,
				]
			)

			update_lora_button.click(
				fn=update_lora,
				inputs=[
					update_lora_name,
				],
				outputs=[
					loras_list,
					lora_text_area,
					lora_preview_md,
					lora_preview_html,
				]
			)
	
	return (modelpreview_interface, "Model Pre​views", "modelpreview_xd_interface"),

def on_ui_settings():
	section = ('model_preview_xd', "Model Preview XD")
	shared.opts.add_option("model_preview_xd_name_matching", shared.OptionInfo("Loose", "Name matching rule for preview files", gr.Radio, {"choices": ["Loose", "Strict", "Folder"]}, section=section))

script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_ui_tabs(on_ui_tabs)