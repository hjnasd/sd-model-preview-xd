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
		spec = importlib.util.find_spec('extensions.sd-webui-additional-networks.scripts.additional_networks')
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

refresh_symbol = '\U0001f504'  # 🔄

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
    return check_dir in dir_list

def list_all_models():
	# gets the list of checkpoints
	model_list = sd_models.checkpoint_tiles()
	return sorted(model_list, key=lambda x: x.lower())

def list_all_embeddings():
	# get the list of embeddings
	list = [x for x in sd_hijack.model_hijack.embedding_db.word_embeddings.keys()]
	list.extend([x for x in sd_hijack.model_hijack.embedding_db.skipped_embeddings.keys()])
	return sorted(list, key=lambda x: x.lower())

def list_all_hypernetworks():
	# get the list of hyperlinks
	list = [x for x in shared.hypernetworks.keys()]
	return sorted(list, key=lambda x: x.lower())
	
def list_all_loras():
	global additional_networks, additional_networks_builtin
	# get the list of lora models
	loras = []

	# import/update the lora module
	additional_networks = import_lora_module()
	if additional_networks is not None:
		# copy the list of models
		loras_list = additional_networks.lora_models.copy()
		# remove the None item from the lsit
		loras_list.pop("None", None)
		loras.extend(loras_list.keys())

	# import/update the builtin lora module
	additional_networks_builtin = import_lora_module_builtin()
	if additional_networks_builtin is not None:
		# copy the list of models
		loras_list = additional_networks_builtin.available_loras.copy()
		# remove the None item from the lsit
		loras_list.pop("None", None)
		loras.extend(loras_list.keys())

	# return the list
	return sorted(loras, key=lambda x: x.lower())

def refresh_models():
	# update the choices for the checkpoint list
	return gr.Dropdown.update(choices=list_all_models())

def refresh_embeddings():
	# update the choices for the embeddings list
	return gr.Dropdown.update(choices=list_all_embeddings())

def refresh_hypernetworks():
	# update the choices for the hypernetworks list
	return gr.Dropdown.update(choices=list_all_hypernetworks())

def refresh_loras():
	# update the choices for the lora list
	return gr.Dropdown.update(choices=list_all_loras())

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

	if is_in_a1111_dir:
		# replace the file name string spaces with %20 so the path will work
		space_replace = file.replace(" ","%20")
		# create the html for the image
		html_code = f'<div class="img-container"><img src=file={space_replace} onclick="imageZoomIn(event)" />'
	else:
		# linking to the image wont work so convert it to a base64 bypte string
		with open(file, "rb") as img_file:
			img_data = base64.b64encode(img_file.read()).decode()
		# create the html for the image
		html_code = f'<div class="img-container"><img src="data:image/{image.format};base64,{img_data}" onclick="imageZoomIn(event)" />'

	# if the image has prompt data in the meta data also add some elements to support copying the prompt to clipboard
	if metadata is not None and metadata.strip() != "":
		html_code += '<div class="img-meta-ico" title="Copy Metadata" onclick="metaDataCopy(event)"></div>'
		html_code += f'<textarea class="img-meta">{metadata}</textarea>'
	html_code += "</div>\n"
	# return the html code
	return html_code


def search_and_display_previews(input_str, paths):
	# create patters for the supported preview file types
	# `input_str` will be the name of the model to check for preview files for
	html_pattern = re.compile(r'.*' + input_str + r'.*\.html')
	md_pattern = re.compile(r'.*' + input_str + r'.*\.md')
	img_pattern = re.compile(r'.*' + input_str + r'.*\.(png|jpg|jpeg|webp)')
	txt_pattern = re.compile(r'.*' + input_str + r'.*\.txt')
	
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
			for file in filenames:
				file_path = os.path.join(dirpath, file)
				if html_pattern.match(file_path):
					# prioritize html files, if you find one, just return it
					return create_html_iframe(file_path, is_in_a1111_dir), None, None
				if md_pattern.match(file_path):
					# there can only be one markdown file, if one was already found it is replaced
					md_file = file_path
				if img_pattern.match(file_path):
					# there can be many images, even spread accross the multiple paths
					html_code_list.append(create_html_img(file_path, is_in_a1111_dir))
				if txt_pattern.match(file_path):
					# there can only be one text file, if one was already found it is replaced
					found_txt_file = file_path
			
	# if there were images found, wrap the images in a container div
	html_code_output = '<div class="img-container-set">' + ''.join(html_code_list) + '</div>' if len(html_code_list) > 0 else None

	# return the images, and/or text file found
	return html_code_output, md_file, found_txt_file

def show_model_preview(modelname=None):
	# remove everything after the last instance of ' [' in the model name and remove .ckpt and .safetensors from the model name
	seperator = ' ['
	modelname = seperator.join(modelname.split(seperator)[:-1]) if modelname.count(seperator) > 0 else modelname
	# create list of directories
	directories = [os.path.join('models','Stable-diffusion')] # models/Stable-diffusion
	set_dir = shared.cmd_opts.ckpt_dir
	if set_dir is not None and not is_dir_in_list(directories, set_dir):
		# WARNING: html files and markdown files that link to local files outside of the automatic1111 directory will not work correctly
		directories.append(set_dir)
	# get preview for the model
	return show_preview(modelname.replace(".ckpt","").replace(".safetensors",""), directories)

def show_embedding_preview(modelname=None):
	# create list of directories
	directories = ['embeddings']
	set_dir = shared.cmd_opts.embeddings_dir
	if set_dir is not None and not is_dir_in_list(directories, set_dir):
		# WARNING: html files and markdown files that link to local files outside of the automatic1111 directory will not work correctly
		directories.append(set_dir)
	# get preview for the model
	return show_preview(modelname, directories)

def show_hypernetwork_preview(modelname=None):
	# create list of directories
	directories = [os.path.join('models','hypernetworks')] # models/hypernetworks
	set_dir = shared.cmd_opts.hypernetwork_dir
	if set_dir is not None and not is_dir_in_list(directories, set_dir):
		# WARNING: html files and markdown files that link to local files outside of the automatic1111 directory will not work correctly
		directories.append(set_dir)
	# remove everything after the last instance of '(' in the model name
	seperator = '('
	modelname = seperator.join(modelname.split(seperator)[:-1]) if modelname.count(seperator) > 0 else modelname
	# get preview for the model
	return show_preview(modelname, directories)

def show_lora_preview(modelname=None):
	directories = []

	# add models/lora just in case to the list of directories
	default_dir = os.path.join("models","lora") # models/lora
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
		directories.append(additional_networks.lora_models_dir)
		set_dir = additional_networks.lora_models_dir
		if set_dir is not None and not is_dir_in_list(directories, set_dir):
			directories.append(set_dir)
		extra_lora_path = shared.opts.data.get("additional_networks_extra_lora_path", None)
		if extra_lora_path and os.path.exists(extra_lora_path) and not is_dir_in_list(directories, extra_lora_path):
			directories.append(extra_lora_path)

	# remove everything after the last instance of '(' in the model name
	seperator = '('
	modelname = seperator.join(modelname.split(seperator)[:-1]) if modelname.count(seperator) > 0 else modelname
	# get preview for the model
	return show_preview(modelname, directories)

def show_preview(name, paths):
	# get the preview data
	html_code, found_md_file, found_txt_file = search_and_display_previews(name, paths)
	preview_html = '' if html_code is None else html_code

	# if a text file was found update the gradio text element
	if found_txt_file:
		with open(found_txt_file, "r", encoding="utf8") as file:
				output_text = ""
				for line in file:
					output_text = f'{output_text}{line.strip()}\n'
		txt_update = gr.Textbox.update(value=output_text, visible=True)
	else:
		txt_update = gr.Textbox.update(value=None, visible=False)
	
	# if a markdown file was found update the gradio markdown element
	if found_md_file:
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
		with gr.Tab("Checkpoints"):
			with gr.Row():
				checkpoints_list = gr.Dropdown(label="Model", choices=list_all_models(), interactive=True, elem_id="cp_mp2_preview_model_list")
				refresh_checkpoint = gr.Button(value=refresh_symbol, elem_id="cp_modelpreview_xd_refresh_sd_model")
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

		# create a tab for the embedding previews
		with gr.Tab("Embeddings"):
			with gr.Row():
				embeddings_list = gr.Dropdown(label="Model", choices=list_all_embeddings(), interactive=True, elem_id="em_mp2_preview_model_list")
				refresh_embedding = gr.Button(value=refresh_symbol, elem_id="em_modelpreview_xd_refresh_sd_model")
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

		# create a tab for the hypernetwork previews
		with gr.Tab("Hypernetwork"):
			with gr.Row():
				hypernetworks_list = gr.Dropdown(label="Model", choices=list_all_hypernetworks(), interactive=True, elem_id="hn_mp2_preview_model_list")
				refresh_hypernetwork = gr.Button(value=refresh_symbol, elem_id="hn_modelpreview_xd_refresh_sd_model")
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

		# create a tab for the lora previews if the module was loaded
		if additional_networks is not None or additional_networks_builtin is not None:
			with gr.Tab("LORA"):
				with gr.Row():
					loras_list = gr.Dropdown(label="Model", choices=list_all_loras(), interactive=True, elem_id="lo_mp2_preview_model_list")
					refresh_lora = gr.Button(value=refresh_symbol, elem_id="lo_modelpreview_xd_refresh_sd_model")
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

	return (modelpreview_interface, "Model Previews", "modelpreview_xd_interface"),

script_callbacks.on_ui_tabs(on_ui_tabs)
