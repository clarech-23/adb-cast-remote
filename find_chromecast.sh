#!/bin/bash

TIMEOUT=60


# Discover Chromecast and extract its IPv4 IP address
get_chromecast_ip_address() {
	# TODO: May need to tweak this command, too hard-coded
	CHROMECAST_IP="$(avahi-browse -rt _googlecast._tcp | \
		grep -E "IPv4|address" | \
		awk '{print $3}' | \
		grep "\." | \
		tr -d '[]')"

	if [[ -z "$CHROMECAST_IP" ]]; then
		echo "No Chromecast found on the local network"
		exit 1
	fi

	echo "Found Chromecast with IP address ${CHROMECAST_IP}"
}


# Attempt to connect to the Chromecast using Android Debug Bridge
attempt_to_connect() {
	adb connect "$CHROMECAST_IP:5555"
}


# Get connection status
get_authorization_status() {
	adb devices | grep -w "$CHROMECAST_IP" | awk '{print $2}'

	# TODO: Throw error if it's not either blank, unauthorized, or device
}


check_timeout_reached() {
	CURRENT_TIME=$(date +%s)
	ELAPSED_TIME=$((CURRENT_TIME - START_TIME))

	if [[ $ELAPSED_TIME -ge TIMEOUT ]]; then
		echo "Exceeded time to pair with Chromecast. Exiting..."
		adb disconnect "$CHROMECAST_IP"
		exit 1
	fi
}


# Connect to the Chromecast using Android Debug Bridge
connect_to_chromecast() {

	echo "Connecting to Chromecast..."
	# TODO: Cover case where there is a syntax error with Chromecast's IP address

	CONNECTION_OUTCOME=$(attempt_to_connect)
	echo "$CONNECTION_OUTCOME"

	if [[ "$CONNECTION_OUTCOME" == *"Connection refused"* ]]; then
		echo "Connection refused. Exiting..."
		exit 1

	elif [[ "$CONNECTION_OUTCOME" == *"failed to authenticate"* || \
		"$CONNECTION_OUTCOME" == *"already connected"* ]]; then
		echo "Please authenticate on Chromecast"

		START_TIME=$(date +%s)
		while [[ "$AUTHORIZATION_STATUS" != "device" ]]; do
			sleep 3

			AUTHORIZATION_STATUS=$(get_authorization_status)
			echo "Auth status: ${AUTHORIZATION_STATUS}"

			check_timeout_reached
		done

		if [[ "$AUTHORIZATION_STATUS" == "device" ]]; then
			echo "Connection authorized! Connected to Chromecast"
			return
		fi

		echo "Unable to connect. Exiting..."
		exit 1

	elif [[ "$CONNECTION_OUTCOME" == "connected to ${CHROMECAST_IP}:5555" ]]; then
		echo "Connection established. No need to authenticate"
		return

	else
		echo "Other connection attempt output: ${CONNECTION_OUTCOME}"
		echo "Exiting..."
		exit 1
	fi
}


# Extract Chromecast's UUID using avahi-browse
get_chromecast_uuid() {
	CHROMECAST_UUID="$(avahi-browse -rt _googlecast._tcp | \
			  grep "hostname" | \
			  awk '{print $3}' | \
			  sort -u | \
			  tr -d '[]')"

	# TODO: What if I don't find a UUID?

	echo "Chromecast's UUID is ${CHROMECAST_UUID}"
}


# Cache the Chromecast's UUID
cache_chromecast_uuid() {
	echo "Remembering Chromecast..."
	printf "${CHROMECAST_UUID}" > chromecast_hostname.txt
	echo "Chromecast remembered as ${CHROMECAST_UUID}"
}

get_chromecast_ip_address
connect_to_chromecast

get_chromecast_uuid
cache_chromecast_uuid
