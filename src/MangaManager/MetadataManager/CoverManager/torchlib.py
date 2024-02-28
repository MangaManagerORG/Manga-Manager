"""
# pip requirements:
# OpenCV-Python
# sentence_transformers
# open_clip_torch
# requests
# git+https://github.com/openai/CLIP.git
# torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

"""
import logging



logger = logging.getLogger()

try:
    # raise ImportError
    import PIL
    import torch
    import open_clip
    from PIL import Image
    from cv2 import cvtColor, COLOR_BGR2RGB
    from numpy import array
    from sentence_transformers import util
    from PIL import Image

    logger.info("Torch libraries successfully imported")
    # image processing model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        logger.warning("Using CUDA")
    model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-16-plus-240', pretrained="laion400m_e32")
    model.to(device)
    def imageEncoder(img):
        img1 = Image.fromarray(img).convert('RGB')
        img1 = preprocess(img1).unsqueeze(0).to(device)
        img1 = model.encode_image(img1)
        return img1


    def generateScore(image1, image2):
        img1 = imageEncoder(image1)
        img2 = imageEncoder(image2)
        cos_scores = util.pytorch_cos_sim(img1, img2)
        score = round(float(cos_scores[0][0]) * 100, 2)
        return score


    def convert_PIL(pil_img: PIL.Image.Image):
        # pil_image = image.convert('RGB')
        # open_cv_image = numpy.array(pil_image)
        # # Convert RGB to BGR
        # return = open_cv_image[:, :, ::-1].copy()
        # cv2_img = numpy.array(pil_img)
        # return cv2.cvtColor(cv2_img, cv2.COLOR_RGB2BGR)
        return cvtColor(array(pil_img), COLOR_BGR2RGB)
except ImportError:
    logger.warning("Missing dependecies for torch. disabling similarity")
    logger.exception("Please install")


    def convert_PIL(*_):
        return None


    def generateScore(*_):
        return 0


    def imageEncoder(*_):
        return None






# if __name__ == '__main__':
# img_rgb = cvtColor(array(Image.open(img)), COLOR_BGR2RGB)
# img_rgb1= cvtColor(array(Image.open(img1)), COLOR_BGR2RGB)
# img_rgb3 = cvtColor(array(Image.open(img3)), COLOR_BGR2RGB)
#
# print(f"similarity Score: ", round(generateScore(img_rgb, img_rgb1), 2))
# print(f"similarity Score: ", round(generateScore(img_rgb, img_rgb3), 2))
# similarity Score: 76.77
