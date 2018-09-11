import os
from django.conf import settings


class AffyMetrixCelWrapper:

    def __init__(self):
        affymetrix_fusion_sdk = os.path.join(settings.BASE_DIR, 'command', 'external_programs', 'affymetrix', 'AffxFusion.jar')
        os.environ['CLASSPATH'] = affymetrix_fusion_sdk
        # it is important to import AFTER setting the CLASSPATH
        from jnius import autoclass
        self._fusionCELDataAutoClass = autoclass('affymetrix.fusion.cel.FusionCELData')
        self.String = autoclass('java.lang.String')