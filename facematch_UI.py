import io
import time

import requests
import streamlit as st
from PIL import Image, ImageOps


API_BASE_URL = "https://api.utils-testing.pagesoft.xyz/api/v1"

REGISTER_URL = f"{API_BASE_URL}/face/register"
ATTENDANCE_URL = f"{API_BASE_URL}/face/attendance"

# Registration image optimization only.
MAX_IMAGE_SIZE = 1024
JPEG_QUALITY = 85

st.set_page_config(
    page_title="FaceMatch Attendance",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.sidebar.title("👤 FaceMatch")

st.sidebar.caption(
    "Face Recognition & Attendance"
)

page = st.sidebar.radio(
    "Select Page",
    [
        "Register Face",
        "Attendance",
    ],
)

st.sidebar.divider()

st.sidebar.caption(
    "API Configuration"
)

st.sidebar.code(
    API_BASE_URL,
    language=None,
)


def format_file_size(size):

    if not size:
        return "Unknown"

    if size < 1024:
        return f"{size} B"

    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"

    return f"{size / (1024 * 1024):.2f} MB"



def prepare_registration_image(
    uploaded_file,
):
    """
    Registration only.

    Registration images are resized/compressed to reduce
    upload size.

    Attendance does NOT use this function.
    """

    uploaded_file.seek(0)

    image = Image.open(
        uploaded_file
    )

    # Apply phone/camera EXIF orientation.
    try:

        image = ImageOps.exif_transpose(
            image
        )

    except Exception:

        pass

    if image.mode != "RGB":

        image = image.convert(
            "RGB"
        )

    original_width, original_height = (
        image.size
    )

    original_size = getattr(
        uploaded_file,
        "size",
        None,
    )

    # Preserve aspect ratio.
    image.thumbnail(
        (
            MAX_IMAGE_SIZE,
            MAX_IMAGE_SIZE,
        ),
        Image.Resampling.LANCZOS,
    )

    processed_width, processed_height = (
        image.size
    )

    output = io.BytesIO()

    image.save(
        output,
        format="JPEG",
        quality=JPEG_QUALITY,
        optimize=True,
    )

    output.seek(0)

    processed_bytes = output.getvalue()

    return {
        "bytes": processed_bytes,
        "filename": "face.jpg",
        "content_type": "image/jpeg",
        "original_width": original_width,
        "original_height": original_height,
        "processed_width": processed_width,
        "processed_height": processed_height,
        "original_size": original_size,
        "processed_size": len(processed_bytes),
    }



def read_original_image(
    uploaded_file,
):

    uploaded_file.seek(0)

    image_bytes = uploaded_file.getvalue()

    filename = getattr(
        uploaded_file,
        "name",
        None,
    )

    if not filename:

        filename = "attendance.jpg"

    content_type = getattr(
        uploaded_file,
        "type",
        None,
    )

    if not content_type:

        content_type = "image/jpeg"

    return {
        "bytes": image_bytes,
        "filename": filename,
        "content_type": content_type,
    }


def process_response(
    response,
):

    try:

        result = response.json()

    except Exception:

        st.error(
            "API returned an invalid response."
        )

        st.code(
            response.text,
            language="text",
        )

        return None

    if response.status_code not in (
        200,
        201,
    ):

        st.error(
            f"API Error: HTTP {response.status_code}"
        )

        with st.expander(
            "API Error Response"
        ):

            st.json(result)

        return None

    return result



def register_face_page():


    st.title(
        "👤 Register Face"
    )

    st.caption(
        "Register a user's face using 3 to 5 images."
    )

    st.divider()


    st.subheader(
        "User Details"
    )

    col1, col2 = st.columns(2)

    with col1:

        user_id = st.number_input(
            "User ID",
            min_value=1,
            value=1,
            step=1,
            key="register_user_id",
        )

    with col2:

        namespace = st.text_input(
            "Namespace",
            placeholder="Example: company_a",
            key="register_namespace",
        )

    st.divider()



    st.subheader(
        "Face Images"
    )

    st.caption(
        "Provide a minimum of 3 and a maximum of 5 face images."
    )

    input_method = st.radio(
        "Choose image source",
        [
            "Upload Images",
            "Take Photos",
        ],
        horizontal=True,
        key="register_input_method",
    )

    images = []


    if input_method == "Upload Images":

        upload_col1, upload_col2, upload_col3 = (
            st.columns(3)
        )

        with upload_col1:

            image1 = st.file_uploader(
                "Face Image 1 *",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                ],
                key="register_image_1",
            )

        with upload_col2:

            image2 = st.file_uploader(
                "Face Image 2 *",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                ],
                key="register_image_2",
            )

        with upload_col3:

            image3 = st.file_uploader(
                "Face Image 3 *",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                ],
                key="register_image_3",
            )

        upload_col4, upload_col5, _ = (
            st.columns(3)
        )

        with upload_col4:

            image4 = st.file_uploader(
                "Face Image 4",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                ],
                key="register_image_4",
            )

        with upload_col5:

            image5 = st.file_uploader(
                "Face Image 5",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                ],
                key="register_image_5",
            )

        uploaded_images = [
            image1,
            image2,
            image3,
            image4,
            image5,
        ]

        images = [
            image
            for image in uploaded_images
            if image is not None
        ]


    else:

        st.info(
            "Take 3 to 5 separate photos. "
            "Keep the face clearly visible."
        )

        camera_col1, camera_col2, camera_col3 = (
            st.columns(3)
        )

        with camera_col1:

            image1 = st.camera_input(
                "Face Image 1 *",
                key="register_camera_1",
            )

        with camera_col2:

            image2 = st.camera_input(
                "Face Image 2 *",
                key="register_camera_2",
            )

        with camera_col3:

            image3 = st.camera_input(
                "Face Image 3 *",
                key="register_camera_3",
            )

        camera_col4, camera_col5, _ = (
            st.columns(3)
        )

        with camera_col4:

            image4 = st.camera_input(
                "Face Image 4",
                key="register_camera_4",
            )

        with camera_col5:

            image5 = st.camera_input(
                "Face Image 5",
                key="register_camera_5",
            )

        camera_images = [
            image1,
            image2,
            image3,
            image4,
            image5,
        ]

        images = [
            image
            for image in camera_images
            if image is not None
        ]


    st.caption(
        f"Images selected: {len(images)} / 5"
    )


    prepared_images = []

    if images:

        st.divider()

        st.subheader(
            "Image Preview"
        )

        st.info(
            "Images are displayed separately to preserve "
            "their orientation."
        )

        for index, image in enumerate(
            images
        ):

            try:

                prepared = prepare_registration_image(
                    image
                )

                prepared_images.append(
                    prepared
                )

                preview_col, details_col = (
                    st.columns(
                        [1, 2]
                    )
                )

                with preview_col:

                    preview_image = Image.open(
                        io.BytesIO(
                            prepared["bytes"]
                        )
                    )

                    st.image(
                        preview_image,
                        caption=(
                            f"Face Image {index + 1}"
                        ),
                        width=260,
                    )

                with details_col:

                    st.write(
                        f"**Face Image {index + 1}**"
                    )

                    st.write(
                        "Original resolution: "
                        f"{prepared['original_width']} × "
                        f"{prepared['original_height']}"
                    )

                    st.write(
                        "Processed resolution: "
                        f"{prepared['processed_width']} × "
                        f"{prepared['processed_height']}"
                    )

                    st.write(
                        "Upload size: "
                        f"{format_file_size(prepared['processed_size'])}"
                    )

                st.divider()

            except Exception as exc:

                st.error(
                    f"Could not process image "
                    f"{index + 1}: {exc}"
                )


    register_clicked = st.button(
        "Register Face",
        type="primary",
        use_container_width=True,
        disabled=(
            len(prepared_images) < 3
            or not namespace.strip()
        ),
        key="register_face_button",
    )

    if not register_clicked:

        return


    if user_id <= 0:

        st.error(
            "User ID must be greater than zero."
        )

        return

    if not namespace.strip():

        st.error(
            "Namespace is required."
        )

        return

    if len(prepared_images) < 3:

        st.error(
            "Please provide at least 3 images."
        )

        return

    if len(prepared_images) > 5:

        st.error(
            "Maximum 5 images are allowed."
        )

        return

    data = {
        "user_id": str(
            int(user_id)
        ),
        "namespace": namespace.strip(),
    }

    files = []

    for index, prepared in enumerate(
        prepared_images
    ):

        files.append(
            (
                "images",
                (
                    f"face_{index + 1}.jpg",
                    prepared["bytes"],
                    "image/jpeg",
                ),
            )
        )

    start_time = time.perf_counter()

    with st.spinner(
        "Registering face..."
    ):

        try:

            response = requests.post(
                REGISTER_URL,
                data=data,
                files=files,
                timeout=180,
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to FastAPI."
            )

            st.code(
                REGISTER_URL,
                language=None,
            )

            return

        except requests.exceptions.Timeout:

            st.error(
                "Registration request timed out."
            )

            return

        except requests.exceptions.RequestException as exc:

            st.error(
                "Registration request failed."
            )

            st.code(
                str(exc),
                language="text",
            )

            return

    elapsed = (
        time.perf_counter()
        - start_time
    )



    result = process_response(
        response
    )

    if result is None:

        return


    st.success(
        "Face registered successfully."
    )

    response_data = result.get(
        "data",
        {},
    )

    st.divider()

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:

        st.metric(
            "User ID",
            response_data.get(
                "user_id",
                user_id,
            ),
        )

    with col2:

        st.metric(
            "Images",
            response_data.get(
                "images_registered",
                len(prepared_images),
            ),
        )

    with col3:

        st.metric(
            "Embedding",
            f"{response_data.get('embedding_dimension', 512)}D",
        )

    with col4:

        st.metric(
            "API Time",
            f"{elapsed:.2f}s",
        )

    st.divider()

    detail_col1, detail_col2 = (
        st.columns(2)
    )

    with detail_col1:

        st.write(
            "Namespace"
        )

        st.code(
            response_data.get(
                "namespace",
                namespace,
            ),
            language=None,
        )

    with detail_col2:

        st.write(
            "Liveness Checked"
        )

        st.write(
            response_data.get(
                "liveness_checked",
                True,
            )
        )

    operation_id = result.get(
        "operation_id"
    )

    if operation_id:

        st.write(
            "Operation ID"
        )

        st.code(
            operation_id,
            language=None,
        )

    with st.expander(
        "API Response"
    ):

        st.json(
            result
        )



def attendance_page():

    st.title(
        "📸 Face Attendance"
    )

    st.caption(
        "Verify a face using liveness detection and "
        "namespace-based face matching."
    )

    st.divider()

    st.subheader(
        "Attendance Details"
    )

    namespace = st.text_input(
        "Namespace",
        placeholder="Example: company_a",
        key="attendance_namespace",
    )

    st.divider()


    st.subheader(
        "Select Image"
    )

    input_method = st.radio(
        "Choose image source",
        [
            "Take Photo",
            "Upload Photo",
        ],
        horizontal=True,
        key="attendance_input_method",
    )

    image = None


    if input_method == "Take Photo":

        image = st.camera_input(
            "Take a photo",
            key="attendance_camera",
        )


    else:

        image = st.file_uploader(
            "Upload a face photo",
            type=[
                "jpg",
                "jpeg",
                "png",
            ],
            key="attendance_upload",
        )


    if image is None:

        st.info(
            "Take a photo or upload a face photo to continue."
        )

        return


    try:

        attendance_image = read_original_image(
            image
        )

    except Exception as exc:

        st.error(
            f"Could not read the image: {exc}"
        )

        return


    st.divider()

    st.subheader(
        "Selected Image"
    )

    preview_col, details_col = (
        st.columns(
            [1, 2]
        )
    )

    with preview_col:


        try:

            preview_image = Image.open(
                io.BytesIO(
                    attendance_image["bytes"]
                )
            )


            try:

                preview_image = ImageOps.exif_transpose(
                    preview_image
                )

            except Exception:

                pass

            st.image(
                preview_image,
                caption="Attendance Image",
                width=300,
            )

        except Exception:

            st.error(
                "Unable to display image preview."
            )

    with details_col:

        st.write(
            "Image Information"
        )

        st.write(
            "Filename: "
            f"{attendance_image['filename']}"
        )

        st.write(
            "Content type: "
            f"{attendance_image['content_type']}"
        )

        st.write(
            "Upload size: "
            f"{format_file_size(len(attendance_image['bytes']))}"
        )

        st.info(
            "The original image bytes will be sent to "
            "the face-matching API without resizing or "
            "compression."
        )

    st.divider()


    attendance_clicked = st.button(
        "Mark Attendance",
        type="primary",
        use_container_width=True,
        disabled=not namespace.strip(),
        key="mark_attendance_button",
    )

    if not attendance_clicked:

        return

    if not namespace.strip():

        st.error(
            "Namespace is required."
        )

        return



    files = {
        "image": (
            attendance_image["filename"],
            attendance_image["bytes"],
            attendance_image["content_type"],
        )
    }


    data = {
        "namespace": namespace.strip(),
    }


    with st.expander(
        "Request Information"
    ):

        st.write(
            "Endpoint:",
            ATTENDANCE_URL,
        )

        st.write(
            "Namespace:",
            namespace.strip(),
        )

        st.write(
            "Filename:",
            attendance_image["filename"],
        )

        st.write(
            "Content type:",
            attendance_image["content_type"],
        )

        st.write(
            "Bytes sent:",
            len(
                attendance_image["bytes"]
            ),
        )


    start_time = time.perf_counter()

    with st.spinner(
        "Checking liveness and matching face..."
    ):

        try:
            response = requests.post(
                ATTENDANCE_URL,
                data=data,
                files=files,
                timeout=180,
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to FastAPI."
            )

            st.code(
                ATTENDANCE_URL,
                language=None,
            )

            return

        except requests.exceptions.Timeout:

            st.error(
                "Attendance request timed out."
            )

            return

        except requests.exceptions.RequestException as exc:

            st.error(
                "Attendance request failed."
            )

            st.code(
                str(exc),
                language="text",
            )

            return

    elapsed = (
        time.perf_counter()
        - start_time
    )


    result = process_response(
        response
    )

    if result is None:

        return

    response_data = result.get(
        "data",
        {},
    )

    matched = response_data.get(
        "matched",
        False,
    )


    if matched:

        st.success(
            "Attendance marked successfully."
        )

        st.divider()

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        # ----------------------------------------------------
        # USER ID
        # ----------------------------------------------------

        with col1:

            st.metric(
                "User ID",
                response_data.get(
                    "user_id",
                    "N/A",
                ),
            )

        # ----------------------------------------------------
        # SIMILARITY
        # ----------------------------------------------------

        with col2:

            similarity = response_data.get(
                "similarity"
            )

            if similarity is not None:

                st.metric(
                    "Similarity",
                    f"{float(similarity):.4f}",
                )

            else:

                st.metric(
                    "Similarity",
                    "N/A",
                )

        with col3:

            distance = response_data.get(
                "distance"
            )

            if distance is not None:

                st.metric(
                    "Distance",
                    f"{float(distance):.4f}",
                )

            else:

                st.metric(
                    "Distance",
                    "N/A",
                )

        with col4:

            st.metric(
                "API Time",
                f"{elapsed:.2f}s",
            )

        st.divider()

        detail_col1, detail_col2 = (
            st.columns(2)
        )

        with detail_col1:

            st.write(
                "Namespace"
            )

            st.code(
                response_data.get(
                    "namespace",
                    namespace,
                ),
                language=None,
            )

        with detail_col2:

            st.write(
                "Liveness Score"
            )

            st.write(
                response_data.get(
                    "liveness_score",
                    "N/A",
                )
            )


        operation_id = result.get(
            "operation_id"
        )

        if operation_id:

            st.write(
                "Operation ID"
            )

            st.code(
                operation_id,
                language=None,
            )

        with st.expander(
            "API Response"
        ):

            st.json(
                result
            )


    else:

        st.warning(
            response_data.get(
                "message",
                "Face not recognized.",
            )
        )

        st.divider()

        col1, col2, col3, col4 = (
            st.columns(4)
        )


        with col1:

            liveness_score = response_data.get(
                "liveness_score"
            )

            st.metric(
                "Liveness",
                (
                    liveness_score
                    if liveness_score is not None
                    else "N/A"
                ),
            )


        with col2:

            similarity = response_data.get(
                "similarity"
            )

            st.metric(
                "Similarity",
                (
                    similarity
                    if similarity is not None
                    else "N/A"
                ),
            )

        with col3:

            threshold = response_data.get(
                "threshold"
            )

            st.metric(
                "Threshold",
                (
                    threshold
                    if threshold is not None
                    else "N/A"
                ),
            )


        with col4:

            st.metric(
                "API Time",
                f"{elapsed:.2f}s",
            )

        st.divider()

        st.write(
            "Namespace searched"
        )

        st.code(
            namespace.strip(),
            language=None,
        )

        with st.expander(
            "API Response"
        ):

            st.json(
                result
            )


if page == "Register Face":

    register_face_page()

elif page == "Attendance":

    attendance_page()
