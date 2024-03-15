<template>
  <div>
    <div role="tablist">
      <!-- General -->
      <div class="panel" role="tab">
        <fx-cert-part-header title="General" v-model="generalShown">
        </fx-cert-part-header>
        <collapse
          id="generalAccordion"
          v-model="generalShown"
        >
          <div class="panel-body info-contents">
            <div v-for="(info, infoindex) in generalInfo" :key="infoindex">
              <div>
                <div class="row" v-for="(item, itemindex) in info.values" :key="itemindex">
                  <data-label class="col-sm-3">{{item.title}}</data-label>
                  <data-label class="col-sm-9">{{item.value}}</data-label>
                </div>
              </div>
            </div>
          </div>
        </collapse>
      </div>
      <!-- Subject -->
      <div class="panel" role="tab">
        <fx-cert-part-header title="Subject" v-model="subjectShown">
        </fx-cert-part-header>
        <collapse
          id="subjectAccordion"
          v-model="subjectShown"
        >
          <div class="panel panel-body info-contents">
            <div class="row" v-for="(attribute, attrindex) in subject" :key="attrindex">
              <data-label class="col-sm-3">{{attribute.name}}</data-label>
              <data-label class="col-sm-9">{{attribute.value}}</data-label>
            </div>
          </div>
        </collapse>
      </div>
      <!-- Extensions -->
      <div
        v-if="extensions.length > 0"
        class="panel"
        role="tab"
      >
        <fx-cert-part-header title="Extensions" v-model="extensionsShown">
        </fx-cert-part-header>
        <collapse
          id="extensionAccordion"
          v-model="extensionsShown"
        >
          <div class="panel-body info-contents">
            <component
              v-for="(extension, index) in extensions"
              :key="index"
              :is="getExtensionComponent(extension)"
              :extension="extension"
            >
            </component>
          </div>
        </collapse>
      </div>
    </div>
  </div>
</template>

<script>
import CertificatePartPanelHeader from './CertificatePartPanelHeader';
import CustomExtension from './extensions/CustomExtension';
import DataLabel from 'kmes/components/misc/DataLabel';
import EncodingUtils from 'shared/EncodingUtils';
import X509ServiceDefs from 'shared/X509ServiceDefs';

export default {
  components: {
    'fx-cert-part-header': CertificatePartPanelHeader,
    'data-label': DataLabel,
  },
  props: {
    cert: {
      type: Object
    },
  },
  data () {
    return {
      generalShown: true,
      subjectShown: false,
      extensionsShown: false,
    };
  },
  computed: {
    subject: function () {
      let subject = [];

      this.cert.tbsCertificate.subject.map(part => {
        const value = EncodingUtils.hexDecode(part.value);

        let dnInfo = X509ServiceDefs.getDirectoryNameTypes().find(dnInfo => {
          return dnInfo.oid === part.oid.split('.').join('_');
        });

        let name = null;
        if (dnInfo) {
          name = dnInfo.name;
        }

        subject.push({
          name: name || 'Unknown',
          value
        });
      });

      return subject;
    },
    generalInfo: function () {
      return [
        {
          section: 'Certificate',
          values: [
            {
              title: 'X.509 Version',
              value: this.cert.tbsCertificate.version,
            },
            {
              title: 'Serial Number',
              value: this.cert.tbsCertificate.serialNumber,
            },
            {
              title: 'Signature Algorithm',
              value: this.getSignatureAlgorithmText(),
            }
          ]
        },
        {
          section: 'Validity Period',
          values: [
            {
              title: 'Not Valid Before',
              value: this.cert.tbsCertificate.validity.notBefore,
            },
            {
              title: 'Not Valid After',
              value: this.cert.tbsCertificate.validity.notAfter,
            }
          ]
        },
        {
          section: 'Public Key',
          values: this.getPublicKeyValues(),
        },
        {
          section: 'Fingerprints',
          values: this.getFingerprints(),
        }
      ];
    },
    extensions: function () {
      return this.cert.tbsCertificate.extensions;
    },
  },
  methods: {
    /**
     * Retrieve the signature algorithm from the certificate.
     *
     * @returns The signature algorithm
     */
    getSignatureAlgorithmText: function () {
      let text = this.cert.signatureAlgorithm.encryptionAlgorithm;
      text += '+';
      text += this.cert.signatureAlgorithm.hashType;

      return text;
    },
    /**
     * Retrieve the extension component.
     *
     * Ideally, any special extension (e.g. Basic Constraints) would have
     * its own component that can optimize how the extension looks.
     *
     * @param {Object} extension - The extension whose component we are getting
     *
     * @returns The component to view the extension
     */
    getExtensionComponent: function (extension) {
      return CustomExtension;
    },
    /**
     * Retrieve the public key display values
     *
     * @returns array of title+value display values
     */
    getPublicKeyValues: function () {
      let values = [];

      let publicKey = this.cert.tbsCertificate.publicKey;
      if (publicKey.type) {
        values.push({
          title: 'Type',
          value: publicKey.type
        });
      }

      if (publicKey.modulus) {
        values.push({
          title: 'Modulus',
          value: publicKey.modulus
        });
      }

      if (publicKey.exponent) {
        values.push({
          title: 'Exponent',
          value: '0x' + publicKey.exponent
        });
      }

      if (publicKey.curve) {
        values.push({
          title: 'Curve',
          value: publicKey.curve
        });
      }

      return values;
    },
    /**
     * Retrieve the fingerprints for the certificate.
     *
     * The fingerprints are just hashes of the full certificate.
     *
     * @returns the certificate fingerprints.
     */
    getFingerprints: function () {
      let fingerprints = [];

      this.cert.fingerprints.map(fingerprint => {
        fingerprints.push({
          title: fingerprint.name,
          value: fingerprint.hash,
        });
      });

      return fingerprints;
    },
  },
};
</script>
