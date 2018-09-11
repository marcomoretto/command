import os
from django.conf import settings


class AffyMetrixCdfWrapper:

    def __init__(self):
        affymetrix_fusion_sdk = os.path.join(settings.BASE_DIR, 'command', 'external_programs', 'affymetrix', 'AffxFusion.jar')
        os.environ['CLASSPATH'] = affymetrix_fusion_sdk
        # it is important to import AFTER setting the CLASSPATH
        from jnius import autoclass
        self._fusionCDFDataAutoClass = autoclass('affymetrix.fusion.cdf.FusionCDFData')
        self._fusionCDFProbeSetInformationAutoClass = autoclass('affymetrix.fusion.cdf.FusionCDFProbeSetInformation')
        self._fusionCDFProbeGroupInformationAutoClass = autoclass('affymetrix.fusion.cdf.FusionCDFProbeGroupInformation')
        self._fusionCDFProbeInformationAutoClass = autoclass('affymetrix.fusion.cdf.FusionCDFProbeInformation')
        self._fusionCDFHeaderAutoClass = autoclass('affymetrix.fusion.cdf.FusionCDFHeader')
        self.String = autoclass('java.lang.String')