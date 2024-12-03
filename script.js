const revoltAPI = "http://local.revolt.chat/api";

/*
	Key: ID in Discord template
	Value: ID in Revolt API

	Example: IDs.roles[discordRoleID] == revoltRoleID
*/
var IDs = {
	roles: [],
	channels: []
};

document.addEventListener("DOMContentLoaded", function() {
	submit.onclick = onSubmit;
});

async function onSubmit() {
	const response = await fetch(templateFetchURL(templateLink.value));
	const tokenIsValidResponse = await fetch(revoltAPI + "/users/@me", {
		headers: authHeader()
	});

	if (!(response.ok && tokenIsValidResponse.ok)) {
		return alert(
			response.ok
			 ? "Token is invalid"
			 : "Server template link is invalid"
		);
	}


	const templateData = await response.json();
	
	const serverName = document.createElement("input");
	serverName.placeholder = "Server name";
	serverName.value = templateData.serialized_source_guild.name;
	
	const serverDescription = document.createElement("textarea");
	serverDescription.placeholder = "Server description";
	serverDescription.value = templateData.serialized_source_guild.description;
	
	document.body.insertBefore(serverName, submit);
	document.body.insertBefore(document.createElement("br"), submit);
	document.body.insertBefore(serverDescription, submit);
	document.body.insertBefore(document.createElement("br"), submit);

	submit.onclick = () => createServer(
		templateData,
		serverName.value,
		serverDescription.value
	);
}

async function createServer(template, name, description) {
	submit.remove();

	const log = document.createElement("pre");
	document.body.append(log);
	
	const allChannels = template.serialized_source_guild.channels;
	/*	
		0 - Text channel
		1 - Voice channel
		4 - Category

		Because Revolt does not has other channel types (eg forum) we will convert textish channel to text channel
	*/
	const channels = allChannels.filter(c => c.type != 4);
	const categories = allChannels.filter(c => c.type == 4);

	log.innerText += "Creating a server...\n";
	
	const revoltServer = await (
		await fetch(revoltAPI + "/servers/create", {
			method: "POST",
			headers: authHeader(),
			body: JSON.stringify({
				name: name,
				description: description
			}),
		})
	).json();

	log.innerText += "Removing server channels...\n";

	revoltServer.channels.forEach(async channel => {
		await fetch(revoltAPI + "/channels/" + channel._id, {
			method: "DELETE",
			headers: authHeader()
		})
	});

	log.innerText += `Creating channels (${channels.length})...\n`;
	var channelsMade = 0;

	await processArray(channels, async channel => {
		log.innerText += `[${channelsMade+1}/${channels.length}] #${channel.name}\n`;
		
		const _ = await fetch(`${revoltAPI}/servers/${revoltServer.server._id}/channels`, {
			method: "POST",
			headers: authHeader(),
			body: JSON.stringify({
				name: channel.name,
				type: channel.type == 2 
						? "Voice"
						: "Text"
			})
		});

		const response = await _.json();
		
		IDs.channels[channel.id] = response._id;
		console.log(IDs.channels);
		channelsMade++;
	})

	console.log(IDs.channels)
	
	log.innerText += `Setting up categories...\n`;

	const revoltCategories = categories.map(category => {
		return {
			id: category.id + "",
			title: category.name,
			channels: channels
				.filter(channel => {
					console.log(channel.parent_id, category.id)
					return channel.parent_id == category.id
				})
				.map(channel => {
					console.log(
						channel.name,
						channel.id,
						IDs.channels[channel.id],
						IDs.channels
					)
					return IDs.channels[channel.id]
				})
		}
	})
	
	console.log(revoltCategories)

	await fetch(revoltAPI + "/servers/" + revoltServer.server._id, {
		method: "PATCH",
		headers: authHeader(),
		body: JSON.stringify({
			categories: revoltCategories
		})
	});

	log.innerText += `Creating roles...\n`;
}

async function processArray(array, func) {
	for (const element of array) {
		await func(element)
	}
}

function templateFetchURL(templateID) {
	if (templateID == "DEMO") return "demo_template.json";

	const templatePath = templateID.split("/");
	
	return "https://discord.com/api/v9/guilds/templates/" + templatePath[templatePath.length-1];
}

function authHeader() {
	return {
		"X-Session-Token": token.value
	}
}
