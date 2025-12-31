/**
 * Universal Hardware Bridge
 * Standardized interface for Thermal Printers and Scales using WebUSB / WebBluetooth
 */
class HardwareBridge {
    constructor() {
        this.device = null;
        this.printerVendorId = null;
        this.status = 'disconnected';
    }

    /**
     * Request connection to a USB Thermal Printer
     */
    async connectPrinter() {
        try {
            // Standard Thermal Printer Vendor IDs (Generic fallback)
            const filters = [
                { vendorId: 0x0483 }, // STM32
                { vendorId: 0x0fe6 }, // Winbond
                { vendorId: 0x1a86 }, // QinHeng Electronics
                { vendorId: 0x0416 }, // Winbond Electronics Corp.
            ];

            this.device = await navigator.usb.requestDevice({ filters });
            await this.device.open();

            // Select configuration and claim interface
            if (this.device.configuration === null) {
                await this.device.selectConfiguration(1);
            }
            await this.device.claimInterface(0);

            this.status = 'connected';
            console.log('[HardwareBridge] Printer connected:', this.device.productName);
            return true;
        } catch (error) {
            console.error('[HardwareBridge] Connection failed:', error);
            return false;
        }
    }

    /**
     * ESC/POS Command Generator
     */
    getCommands() {
        return {
            INIT: '\x1B\x40',
            ALIGN_CENTER: '\x1B\x61\x01',
            ALIGN_LEFT: '\x1B\x61\x00',
            ALIGN_RIGHT: '\x1B\x61\x02',
            BOLD_ON: '\x1B\x45\x01',
            BOLD_OFF: '\x1B\x45\x00',
            CUT: '\x1D\x56\x01',
            TEXT_SIZE_LARGE: '\x1D\x21\x11',
            TEXT_SIZE_NORMAL: '\x1D\x21\x00',
            FEED_LINES: (n) => `\x1B\x64${String.fromCharCode(n)}`,
        };
    }

    /**
     * Print Raw Text / ESC/POS commands
     */
    async printRaw(data) {
        if (!this.device) throw new Error('No device connected');

        const encoder = new TextEncoder();
        const bytes = typeof data === 'string' ? encoder.encode(data) : data;

        // Find bulk out endpoint
        const endpoint = this.device.configuration.interfaces[0].alternate.endpoints.find(
            e => e.direction === 'out' && e.type === 'bulk'
        );

        if (!endpoint) throw new Error('Proper endpoint not found');

        await this.device.transferOut(endpoint.endpointNumber, bytes);
    }

    /**
     * High-level Receipt Printing Example
     */
    async printReceipt(receiptData) {
        const cmd = this.getCommands();
        let data = cmd.INIT + cmd.ALIGN_CENTER + cmd.TEXT_SIZE_LARGE + cmd.BOLD_ON;
        data += `${receiptData.tenant_name}\n`;
        data += cmd.TEXT_SIZE_NORMAL + cmd.BOLD_OFF;
        data += `${receiptData.branch_name}\n`;
        data += `--------------------------------\n`;
        data += cmd.ALIGN_LEFT;

        receiptData.items.forEach(item => {
            const line = `${item.name.padEnd(20)} ${item.price.padStart(10)}\n`;
            data += line;
        });

        data += `--------------------------------\n`;
        data += cmd.ALIGN_RIGHT + cmd.BOLD_ON;
        data += `TOTAL: ${receiptData.total}\n`;
        data += cmd.FEED_LINES(3) + cmd.CUT;

        await this.printRaw(data);
    }
}

// Global instance
window.hardwareBridge = new HardwareBridge();
