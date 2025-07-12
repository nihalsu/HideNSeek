# HideNSeek – Web App for Hiding Secret Messages in Images

### HideNSeek is a web-based steganography tool that allows users to hide secret text messages inside images and later extract them when needed. It uses the Least Significant Bit (LSB) manipulation technique to embed data invisibly into image pixels.

### With this project, you can:
### Embed secret messages into any PNG or BMP image.
### Extract previously hidden messages directly from the same web interface.
### Automatically adjust message capacity based on image resolution.
### It's a simple, fast, and intuitive way to encrypt your words within an image — both for privacy and fun!

## Encode Page

<img width="1903" height="897" alt="Ekran görüntüsü 2025-07-12 152228" src="https://github.com/user-attachments/assets/ead529e2-beac-48ec-a609-ae71870533f4" />

### if histogram equalization is used:

<img width="1901" height="895" alt="Ekran görüntüsü 2025-07-12 153034" src="https://github.com/user-attachments/assets/32810f1f-7122-4200-8232-48d87905d231" />

### else:

<img width="1892" height="887" alt="Ekran görüntüsü 2025-07-12 153125" src="https://github.com/user-attachments/assets/f840d460-6263-4e5e-8c70-caf8449eab66" />
<img width="1900" height="897" alt="Ekran görüntüsü 2025-07-12 153042" src="https://github.com/user-attachments/assets/15a11859-4855-4f69-873e-648ec6a2eadd" />

The Encode page allows users to upload an image (preferably PNG or BMP) and embed a secret message within it using the Least Significant Bit (LSB) steganography technique. Once an image is selected, it is previewed in real-time, and the message input area dynamically displays what will be hidden. The "Create" button initiates the encoding process by sending the image and message to the Flask backend using a FormData POST request.

An optional checkbox allows users to apply histogram equalization before encoding. This enhances the contrast of the image, which can help distribute pixel intensities more uniformly. While it doesn’t improve the steganographic strength directly, it may reduce visual artifacts and make hidden data less detectable in flat-colored images.

The server responds with a modified preview image containing the hidden message, download links, and several useful statistics such as message length, number of used bits, and total color channels. Additionally, the bitplanes (binary representations of each bit layer in the image) are displayed to visualize which bit levels were modified. A "Compare" button is provided to open a new tab and compare the original and encoded images side by side.

This page combines usability and low-level control, giving both technical insight and practical functionality for digital steganography.

<img width="1919" height="880" alt="Ekran görüntüsü 2025-07-12 153146" src="https://github.com/user-attachments/assets/5a598236-c79d-43fe-9062-2af4a0818c97" />

The Compare page (compare.html) provides a side-by-side visual comparison of the original image and the encoded image with the hidden message. This feature is useful for evaluating the visual impact of the steganography process and verifying that no significant artifacts have been introduced.

When encoding is complete, the application dynamically passes both image URLs (original and encoded) as query parameters to this page. The images are displayed side by side in the browser for quick inspection. This feature is especially helpful in demonstrating how LSB-based steganography modifies images subtly — often imperceptibly to the human eye.

The Compare page enhances transparency and allows users to visually validate the integrity of their encoded content.


## Decode Page

<img width="1903" height="897" alt="Ekran görüntüsü 2025-07-12 152228" src="https://github.com/user-attachments/assets/8a96fcc0-6904-4731-aa33-8b40c9045a9d" />

The Decode page allows users to upload an image and extract a hidden message embedded within it, assuming the image was previously processed by the application. Upon selecting an image, a preview is displayed. When the "Decode" button is clicked, the selected image is sent to the Flask backend using a FormData POST request.

The server attempts to locate and decode any hidden message from the image using LSB-based steganography. If successful, the hidden message is displayed in a result container. If no message is found or an error occurs, an appropriate message is shown to the user.

This page is designed to provide a minimal and clear interface for decoding steganographic content, making it accessible for both general users and technical demonstrations.

## Technical Background 
The steganography.py module contains the core logic for hiding and extracting messages within images using Least Significant Bit (LSB) steganography.

### Encoding Process
The encode_message function takes an image and a message as input. It first computes an edge mask using the Canny edge detector, so that the message is not hidden in edge regions where visual distortions are more noticeable. The message is converted to binary, appended with a special 16-bit delimiter (1111111111111110), and embedded into the RGB channels of the image pixel-by-pixel. Only the least significant bit of each color channel is modified.

An optional histogram equalization step (handled in the main Flask app) can be applied to enhance contrast and distribute pixel intensities more evenly, which may help reduce detectability.

### Bitplane Visualization
The extract_bit_planes function generates separate grayscale images for each bit layer (from bit 0 to 7). This helps users visualize how LSB encoding alters the image — usually only the 0th bit plane shows subtle changes.

### Decoding Process
The decode_message function iterates over the least significant bits of all color channels to reconstruct the binary message. Once it detects the predefined delimiter, it stops and converts the binary back into UTF-8 text.

If the delimiter is not found, it returns an error indicating that no message was likely hidden in the image.

This backend design ensures:
 - Minimal visual distortion
 - High data embedding efficiency
 - Edge-aware steganography for robustness

